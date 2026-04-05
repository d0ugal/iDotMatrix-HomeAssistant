"""DataUpdateCoordinator for iDotMatrix — owns all display logic."""

from __future__ import annotations

import asyncio
import hashlib
import io
import logging
import os
import tempfile
import time
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from PIL import Image as PilImage

from .const import (
    DISPLAY_MODE_EMOJI,
    DISPLAY_MODE_IMAGE,
    DISPLAY_MODE_MOON,
    DISPLAY_MODE_NOW_PLAYING,
    DISPLAY_MODE_STREAM,
    DOMAIN,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

SCREEN_SIZE = 64


def _crop_and_resize(img: PilImage.Image, size: int) -> PilImage.Image:
    """Centre-crop to square then resize to size×size."""
    w, h = img.size
    m = min(w, h)
    left = (w - m) // 2
    top = (h - m) // 2
    return img.crop((left, top, left + m, top + m)).resize((size, size), PilImage.LANCZOS)


def _compute_moon_attrs(lat: str, lon: str, elev: int) -> dict:
    """Return a dict of moon stats for the current moment."""
    import ephem

    obs = ephem.Observer()
    obs.lat = lat
    obs.lon = lon
    obs.elevation = float(elev)
    obs.date = ephem.now()

    moon = ephem.Moon(obs)
    moon.compute(obs)

    age = float(obs.date - ephem.previous_new_moon(obs.date))
    waxing = age < 14.77
    pct = moon.phase

    if pct < 2:
        phase = "New Moon"
    elif pct < 45:
        phase = "Waxing Crescent" if waxing else "Waning Crescent"
    elif pct < 55:
        phase = "First Quarter" if waxing else "Last Quarter"
    elif pct < 98:
        phase = "Waxing Gibbous" if waxing else "Waning Gibbous"
    else:
        phase = "Full Moon"

    try:
        rise = ephem.localtime(obs.next_rising(ephem.Moon())).isoformat()
        setting = ephem.localtime(obs.next_setting(ephem.Moon())).isoformat()
    except Exception:
        rise = None
        setting = None

    return {
        "moon_phase": phase,
        "moon_illumination": round(pct, 1),
        "moon_altitude_deg": round(float(moon.alt) * 57.2958, 1),
        "moon_next_rise": rise,
        "moon_next_set": setting,
    }


class IDotMatrixCoordinator(DataUpdateCoordinator):
    """Coordinator: polls BLE status, owns all display render/upload logic."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.entry = entry
        self._store = Store(hass, STORAGE_VERSION, f"idotmatrix_{entry.entry_id}")

        # Current display state — read by light entity
        self.display_mode: str | None = None
        self.display_attrs: dict = {}
        self.screen_on: bool = True
        self.brightness: int = 128  # HA scale 0-255

        # Timestamp of last successful upload — read by sensor
        self.last_updated: str | None = None

        # Persisted default (replayed on light.turn_on and HA restart)
        self._default_mode: str | None = None
        self._default_attrs: dict = {}

        # Cancel handle for display_for revert timer
        self._revert_unsub = None

        # Running stream task (if any)
        self._stream_task: asyncio.Task | None = None

    # ------------------------------------------------------------------
    # DataUpdateCoordinator

    async def _async_update_data(self) -> dict:
        """Poll BLE connection status."""
        try:
            from .client.connectionManager import ConnectionManager

            cm = ConnectionManager()
            connected = cm.client is not None and cm.client.is_connected
        except Exception:
            connected = False
        return {"connected": connected}

    # ------------------------------------------------------------------
    # Persistence

    async def async_load_and_replay(self) -> None:
        """Load persisted state on startup and replay the default display."""
        stored = await self._store.async_load() or {}
        self._default_mode = stored.get("mode")
        self._default_attrs = stored.get("attrs", {})
        self.brightness = stored.get("brightness", 128)
        if self._default_mode:
            _LOGGER.info("Replaying persisted default: %s", self._default_mode)
            await self._replay_default()

    async def _save(self) -> None:
        await self._store.async_save(
            {
                "mode": self._default_mode,
                "attrs": self._default_attrs,
                "brightness": self.brightness,
            }
        )

    # ------------------------------------------------------------------
    # display_for timer

    def cancel_stream(self) -> None:
        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()
        self._stream_task = None

    def cancel_revert(self) -> None:
        if self._revert_unsub:
            self._revert_unsub()
            self._revert_unsub = None

    def schedule_revert(self, seconds: float) -> None:
        """Revert to default display after `seconds`."""
        self.cancel_revert()

        @callback
        def _cb(_now):
            self.hass.async_create_task(self._replay_default())

        self._revert_unsub = async_call_later(self.hass, seconds, _cb)

    async def _replay_default(self) -> None:
        """Re-run the stored default display."""
        self._revert_unsub = None
        mode = self._default_mode
        attrs = self._default_attrs
        if mode == DISPLAY_MODE_MOON:
            await self.do_display_moon(set_default=False)
        elif mode == DISPLAY_MODE_NOW_PLAYING:
            entity_id = attrs.get("entity_id")
            if entity_id:
                await self.do_display_now_playing(entity_id, set_default=False)
        elif mode == DISPLAY_MODE_IMAGE:
            path = attrs.get("path")
            if path:
                await self.do_display_image(path, set_default=False)
        elif mode == DISPLAY_MODE_EMOJI:
            char = attrs.get("char")
            if char:
                await self.do_display_emoji(char, set_default=False)

    # ------------------------------------------------------------------
    # Internal helpers

    def _mark_updated(self, mode: str, attrs: dict) -> None:
        self.display_mode = mode
        self.display_attrs = dict(attrs)
        self.last_updated = dt_util.now().isoformat()
        self.async_set_updated_data(self.data or {"connected": False})

    def _gif_cache_dir(self) -> str:
        return self.hass.config.path(".storage", "idotmatrix_gif_cache")

    async def _upload_gif(self, gif_path: str) -> bool:
        from .client.connectionManager import ConnectionManager
        from .client.modules.gif import Gif as IDMGif

        ok = await IDMGif().uploadSingleRaw(gif_path)
        if not ok:
            # GATT errors can leave the client in a stale connected state.
            # Force a fresh connection and retry once.
            _LOGGER.warning("GIF upload failed, forcing reconnect and retrying: %s", gif_path)
            conn = ConnectionManager()
            try:
                await conn.disconnect()
            except Exception:
                pass
            conn.client = None
            ok = await IDMGif().uploadSingleRaw(gif_path)
        if not ok:
            _LOGGER.error("GIF upload failed after retry: %s", gif_path)
        return ok

    # ------------------------------------------------------------------
    # Display services

    async def do_display_moon(
        self,
        display_for: float | None = None,
        set_default: bool = True,
    ) -> None:
        """Render moon phase and upload as GIF."""
        self.cancel_stream()
        from .moon import render_image

        lat = str(self.hass.config.latitude)
        lon = str(self.hass.config.longitude)
        elev = int(self.hass.config.elevation or 0)

        def _render_gif() -> bytes:
            img = render_image(lat, lon, elev)
            gif_img = img.quantize(colors=256)
            buf = io.BytesIO()
            gif_img.save(buf, format="GIF", loop=0, disposal=2)
            return buf.getvalue()

        gif_data = await self.hass.async_add_executor_job(_render_gif)

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
            tmp.write(gif_data)
            tmp_path = tmp.name

        try:
            ok = await self._upload_gif(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        if not ok:
            return

        moon_attrs = await self.hass.async_add_executor_job(_compute_moon_attrs, lat, lon, elev)

        if set_default and not display_for:
            self._default_mode = DISPLAY_MODE_MOON
            self._default_attrs = {}
            await self._save()

        if display_for:
            self.schedule_revert(display_for)
        else:
            self.cancel_revert()

        self._mark_updated(DISPLAY_MODE_MOON, moon_attrs)
        _LOGGER.info(
            "display_moon: uploaded (%s, %.1f%% illuminated)",
            moon_attrs.get("moon_phase"),
            moon_attrs.get("moon_illumination", 0),
        )

    async def do_display_now_playing(
        self,
        entity_id: str,
        display_for: float | None = None,
        set_default: bool = True,
    ) -> None:
        """Fetch album art from a media player and upload as now-playing GIF."""
        self.cancel_stream()
        import aiohttp
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        from .overlay import render_now_playing_frames

        state = self.hass.states.get(entity_id)
        if not state:
            _LOGGER.error("display_now_playing: entity %s not found", entity_id)
            return

        track = state.attributes.get("media_title") or ""
        artist = state.attributes.get("media_artist") or ""
        entity_picture = state.attributes.get("entity_picture")

        if not entity_picture and not track and not artist:
            _LOGGER.debug("display_now_playing: skipping %s — no artwork or metadata", entity_id)
            return

        cache_dir = self._gif_cache_dir()
        cache_key = hashlib.md5(f"{track}|{artist}|{entity_picture or ''}".encode()).hexdigest()
        gif_path = os.path.join(cache_dir, f"{cache_key}.gif")

        if not os.path.exists(gif_path):
            img = None
            if entity_picture:
                try:
                    session = async_get_clientsession(self.hass)
                    url = (
                        entity_picture
                        if entity_picture.startswith("http")
                        else f"http://localhost:8123{entity_picture}"
                    )
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            raw = await resp.read()
                            img = await self.hass.async_add_executor_job(
                                lambda: (
                                    PilImage.open(io.BytesIO(raw))
                                    .convert("RGB")
                                    .resize((SCREEN_SIZE, SCREEN_SIZE), PilImage.LANCZOS)
                                )
                            )
                except Exception as exc:
                    _LOGGER.warning("display_now_playing: art fetch failed: %s", exc)

            if img is None:
                img = PilImage.new("RGB", (SCREEN_SIZE, SCREEN_SIZE), (0, 0, 0))

            def _render_and_cache() -> None:
                frames_data = render_now_playing_frames(img, track, artist)
                frames = [f for f, _ in frames_data]
                durations = [d for _, d in frames_data]
                _LOGGER.info(
                    "display_now_playing: rendering '%s' by '%s' — %d frames",
                    track,
                    artist,
                    len(frames),
                )
                palette = frames[0].quantize(colors=32)
                frames_p = [f.quantize(palette=palette) for f in frames]
                buf = io.BytesIO()
                if len(frames_p) == 1:
                    frames_p[0].save(buf, format="GIF", loop=0, disposal=2)
                else:
                    frames_p[0].save(
                        buf,
                        format="GIF",
                        save_all=True,
                        append_images=frames_p[1:],
                        loop=0,
                        duration=durations,
                        disposal=2,
                    )
                os.makedirs(cache_dir, exist_ok=True)
                with open(gif_path, "wb") as f:
                    f.write(buf.getvalue())

            await self.hass.async_add_executor_job(_render_and_cache)
            _LOGGER.info("display_now_playing: rendered and cached (%s)", cache_key[:8])
        else:
            _LOGGER.info("display_now_playing: cache hit (%s)", cache_key[:8])

        gif_size = os.path.getsize(gif_path)
        _LOGGER.info(
            "display_now_playing: uploading '%s' by '%s' — %.1f KB",
            track,
            artist,
            gif_size / 1024,
        )

        if not await self._upload_gif(gif_path):
            return

        attrs = {
            "media_entity": entity_id,
            "media_title": track,
            "media_artist": artist,
        }

        if set_default and not display_for:
            self._default_mode = DISPLAY_MODE_NOW_PLAYING
            self._default_attrs = {"entity_id": entity_id}
            await self._save()

        if display_for:
            self.schedule_revert(display_for)
        else:
            self.cancel_revert()

        self._mark_updated(DISPLAY_MODE_NOW_PLAYING, attrs)
        _LOGGER.info("display_now_playing: uploaded — %s by %s", track, artist)

    async def do_display_image(
        self,
        path: str | None = None,
        entity_id: str | None = None,
        display_for: float | None = None,
        set_default: bool = True,
    ) -> None:
        """Crop/resize any image or GIF to 64×64 and upload.

        Supply either `path` (local file) or `entity_id` (camera entity).
        Camera snapshots are always fetched fresh and not cached.
        """
        self.cancel_stream()
        cache_dir = self._gif_cache_dir()

        if entity_id is not None:
            # --- camera entity path: fetch snapshot via internal HA API, no caching ---
            from homeassistant.components.camera import async_get_image

            try:
                img_obj = await async_get_image(self.hass, entity_id, timeout=10)
                raw = img_obj.content
            except Exception as exc:
                _LOGGER.error("display_image: camera snapshot error for %s: %s", entity_id, exc)
                return

            def _process_camera() -> bytes:
                img = PilImage.open(io.BytesIO(raw)).convert("RGB")
                frame = _crop_and_resize(img, SCREEN_SIZE)
                palette = frame.quantize(colors=256)
                buf = io.BytesIO()
                palette.save(buf, format="GIF", loop=0, disposal=2)
                return buf.getvalue()

            gif_data = await self.hass.async_add_executor_job(_process_camera)
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
                tmp.write(gif_data)
                tmp_path = tmp.name

            try:
                ok = await self._upload_gif(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            if not ok:
                return

            attrs = {"entity_id": entity_id}
            if set_default and not display_for:
                self._default_mode = DISPLAY_MODE_IMAGE
                self._default_attrs = {"entity_id": entity_id}
                await self._save()

        else:
            # --- local file path: cache by mtime ---
            if path is None:
                _LOGGER.error("display_image: neither path nor entity_id provided")
                return
            if not os.path.exists(path):
                _LOGGER.error("display_image: file not found: %s", path)
                return

            stat = os.stat(path)
            cache_key = hashlib.md5(f"{path}:{stat.st_mtime}".encode()).hexdigest()
            gif_path = os.path.join(cache_dir, f"{cache_key}.gif")

            if not os.path.exists(gif_path):

                def _process() -> None:
                    with PilImage.open(path) as src:
                        is_anim = getattr(src, "n_frames", 1) > 1
                        default_delay = src.info.get("duration", 100)
                        frames, durations = [], []
                        try:
                            while True:
                                frame = _crop_and_resize(src.copy().convert("RGB"), SCREEN_SIZE)
                                frames.append(frame)
                                durations.append(src.info.get("duration", default_delay))
                                if not is_anim:
                                    break
                                src.seek(src.tell() + 1)
                        except EOFError:
                            pass

                        palette = frames[0].quantize(colors=256)
                        frames_p = [f.quantize(palette=palette) for f in frames]
                        buf = io.BytesIO()
                        if len(frames_p) == 1:
                            frames_p[0].save(buf, format="GIF", loop=0, disposal=2)
                        else:
                            frames_p[0].save(
                                buf,
                                format="GIF",
                                save_all=True,
                                append_images=frames_p[1:],
                                loop=0,
                                duration=durations,
                                disposal=2,
                            )
                        os.makedirs(cache_dir, exist_ok=True)
                        with open(gif_path, "wb") as f:
                            f.write(buf.getvalue())

                await self.hass.async_add_executor_job(_process)

            if not await self._upload_gif(gif_path):
                return

            attrs = {"path": path}
            if set_default and not display_for:
                self._default_mode = DISPLAY_MODE_IMAGE
                self._default_attrs = {"path": path}
                await self._save()

        if display_for:
            self.schedule_revert(display_for)
        else:
            self.cancel_revert()

        self._mark_updated(DISPLAY_MODE_IMAGE, attrs)
        _LOGGER.info("display_image: uploaded %s", entity_id or path)

    async def do_display_emoji(
        self,
        emoji_input: str,
        display_for: float | None = None,
        set_default: bool = True,
        line1: str | None = None,
        line2: str | None = None,
    ) -> None:
        """Fetch a Twemoji PNG, resize to 64×64, and upload."""
        self.cancel_stream()
        import aiohttp
        import emoji as emoji_lib
        from homeassistant.helpers.aiohttp_client import async_get_clientsession

        # Resolve name → character. Accept: raw emoji ("🔔"), bare name ("bell"),
        # or colon-wrapped name (":bell:") — all produce the same character.
        raw = emoji_input.strip()
        if emoji_lib.is_emoji(raw):
            char = raw
        else:
            name = raw.strip(":")
            char = emoji_lib.emojize(f":{name}:", language="alias")
            if not emoji_lib.is_emoji(char):
                _LOGGER.error("display_emoji: unknown emoji %r", emoji_input)
                return

        # Build Twemoji filename: codepoints joined by "-", skipping U+FE0F
        # (variation selector-16) which Twemoji omits from most filenames.
        codepoints = "-".join(f"{ord(c):x}" for c in char if c != "\ufe0f")
        cache_dir = self._gif_cache_dir()
        gif_path = os.path.join(cache_dir, f"emoji_{codepoints}.gif")

        if not os.path.exists(gif_path):
            base_url = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72"
            session = async_get_clientsession(self.hass)

            png_data: bytes | None = None
            for candidate in [codepoints, codepoints.replace("-fe0f", "")]:
                try:
                    async with session.get(
                        f"{base_url}/{candidate}.png",
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            png_data = await resp.read()
                            break
                except Exception as exc:
                    _LOGGER.debug("display_emoji: fetch attempt failed: %s", exc)

            if not png_data:
                _LOGGER.error(
                    "display_emoji: could not fetch Twemoji for %r (%s)", char, codepoints
                )
                return

            def _render() -> None:
                img = PilImage.open(io.BytesIO(png_data)).convert("RGBA")
                # Paste onto black background (GIF has no alpha)
                bg = PilImage.new("RGB", img.size, (0, 0, 0))
                bg.paste(img, mask=img.split()[3])
                resized = bg.resize((SCREEN_SIZE, SCREEN_SIZE), PilImage.LANCZOS)
                quantized = resized.quantize(colors=256)
                buf = io.BytesIO()
                quantized.save(buf, format="GIF", loop=0, disposal=2)
                os.makedirs(cache_dir, exist_ok=True)
                with open(gif_path, "wb") as f:
                    f.write(buf.getvalue())

            await self.hass.async_add_executor_job(_render)
            _LOGGER.info("display_emoji: rendered and cached %r (%s)", char, codepoints)
        else:
            _LOGGER.info("display_emoji: cache hit %r (%s)", char, codepoints)

        if line1 or line2:
            def _apply_overlay() -> bytes:
                from .overlay import apply_now_playing_overlay

                with PilImage.open(gif_path) as src:
                    frame = src.convert("RGB")
                apply_now_playing_overlay(frame, line1 or "", line2 or "")
                buf = io.BytesIO()
                frame.quantize(colors=256).save(buf, format="GIF", loop=0, disposal=2)
                return buf.getvalue()

            overlay_data = await self.hass.async_add_executor_job(_apply_overlay)
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
                tmp.write(overlay_data)
                upload_path = tmp.name
            try:
                ok = await self._upload_gif(upload_path)
            finally:
                if os.path.exists(upload_path):
                    os.remove(upload_path)
        else:
            ok = await self._upload_gif(gif_path)

        if not ok:
            return

        attrs = {"char": char, "codepoints": codepoints}

        if set_default and not display_for:
            self._default_mode = DISPLAY_MODE_EMOJI
            self._default_attrs = {"char": char}
            await self._save()

        if display_for:
            self.schedule_revert(display_for)
        else:
            self.cancel_revert()

        self._mark_updated(DISPLAY_MODE_EMOJI, attrs)
        _LOGGER.info("display_emoji: uploaded %r", char)

    async def do_display_stream(
        self,
        entity_id: str,
        stream_for: float,
    ) -> None:
        """Repeatedly snapshot a camera entity and push frames over BLE.

        Runs until `stream_for` seconds have elapsed or another display
        action cancels the stream.  Always reverts to the default display
        when done.
        """
        self.cancel_stream()
        self.cancel_revert()
        self._mark_updated(DISPLAY_MODE_STREAM, {"entity_id": entity_id, "stream_for": stream_for})
        self._stream_task = self.hass.async_create_task(self._run_stream(entity_id, stream_for))

    async def _run_stream(self, entity_id: str, stream_for: float) -> None:
        """Inner loop for do_display_stream — runs as a background task."""
        from homeassistant.components.camera import async_get_image

        deadline = time.monotonic() + stream_for
        frames_sent = 0
        completed = False

        try:
            while time.monotonic() < deadline:
                try:
                    img_obj = await async_get_image(self.hass, entity_id, timeout=10)
                    raw = img_obj.content
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    _LOGGER.warning("display_stream: snapshot error for %s: %s", entity_id, exc)
                    await asyncio.sleep(1)
                    continue

                def _process(data: bytes = raw) -> bytes:
                    img = PilImage.open(io.BytesIO(data)).convert("RGB")
                    frame = _crop_and_resize(img, SCREEN_SIZE)
                    palette = frame.quantize(colors=256)
                    buf = io.BytesIO()
                    palette.save(buf, format="GIF", loop=0, disposal=2)
                    return buf.getvalue()

                gif_data = await self.hass.async_add_executor_job(_process)

                with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
                    tmp.write(gif_data)
                    tmp_path = tmp.name

                try:
                    await self._upload_gif(tmp_path)
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

                frames_sent += 1
                await asyncio.sleep(1)

            completed = True
        except asyncio.CancelledError:
            pass
        finally:
            self._stream_task = None
            _LOGGER.info(
                "display_stream: %s — %d frames sent",
                "completed" if completed else "cancelled",
                frames_sent,
            )

        if completed:
            await self._replay_default()

    # ------------------------------------------------------------------
    # Screen power and brightness

    async def do_screen_on(self) -> None:
        from .client.modules.common import Common

        await Common().screenOn()
        self.screen_on = True
        self.async_set_updated_data(self.data or {"connected": False})

    async def do_screen_off(self) -> None:
        from .client.modules.common import Common

        await Common().screenOff()
        self.screen_on = False
        self.async_set_updated_data(self.data or {"connected": False})

    async def do_set_brightness(self, brightness_ha: int) -> None:
        """Set brightness. brightness_ha is 0-255 (HA scale); device takes 5-100%."""
        from .client.modules.common import Common

        pct = max(5, round(brightness_ha / 255 * 100))
        await Common().setBrightness(pct)
        self.brightness = brightness_ha
        await self._save()
        self.async_set_updated_data(self.data or {"connected": False})
