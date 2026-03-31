"""Moon phase renderer for the iDotMatrix 64x64 display.

Ported from moon/render.py. Returns a PIL Image rather than writing files.
Location and aurora state are injected at call time.
"""

from __future__ import annotations

import math
import os

from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────

SIZE = 64
CX, CY = 31.5, 31.5
RADIUS = 30

BG = (0, 0, 0)
RING_ON = (60, 60, 60)
HORIZON_GLOW_DEG = 8
LUNAR_CYCLE = 29.53
EVENT_LABEL_DAYS = 7  # show label only within this many days of an event

# Set True when the display is on a north-facing wall (mirrors east↔west).
MIRROR_EW = True

_TEXTURE_PATH = os.path.join(os.path.dirname(__file__), "lune.png")
_texture = None


def _load_texture():
    global _texture
    if _texture is None:
        _texture = Image.open(_TEXTURE_PATH).convert("L").load()
    return _texture


# ── Astronomy ─────────────────────────────────────────────────────────────────


def observe(lat: str, lon: str, elev: int, dt=None) -> dict:
    """Return moon data for the given location at the given time (or now)."""
    import ephem

    obs = ephem.Observer()
    obs.lat, obs.lon, obs.elevation = lat, lon, elev
    if dt is not None:
        obs.date = dt
    moon = ephem.Moon(obs)
    sun = ephem.Sun(obs)
    age = float(obs.date - ephem.previous_new_moon(obs.date))
    alt = math.degrees(float(moon.alt))

    chi = math.atan2(
        math.cos(float(sun.a_dec)) * math.sin(float(sun.a_ra) - float(moon.a_ra)),
        math.sin(float(sun.a_dec)) * math.cos(float(moon.a_dec))
        - math.cos(float(sun.a_dec))
        * math.sin(float(moon.a_dec))
        * math.cos(float(sun.a_ra) - float(moon.a_ra)),
    )
    rotation = float(moon.parallactic_angle()) - chi

    try:
        transit_obs = obs.copy()
        transit_obs.date = obs.next_transit(ephem.Moon())
        transit_moon = ephem.Moon(transit_obs)
        peak_alt = max(1.0, math.degrees(float(transit_moon.alt)))
    except Exception:
        peak_alt = 60.0

    rise_fraction = None
    if alt <= 0:
        try:
            prev_set = float(obs.previous_setting(ephem.Moon()))
            next_rise = float(obs.next_rising(ephem.Moon()))
            total = next_rise - prev_set
            elapsed = float(obs.date) - prev_set
            rise_fraction = max(0.0, min(1.0, elapsed / total))
        except Exception:
            rise_fraction = 0.0

    return {
        "age": age,
        "pct": moon.phase,
        "alt": alt,
        "az": math.degrees(float(moon.az)),
        "rise_fraction": rise_fraction,
        "peak_alt": peak_alt,
        "rotation": rotation,
    }


# ── Moon disc ─────────────────────────────────────────────────────────────────


def _terminator_d(nx, ny, age):
    phase = (age % 29.5) / 29.5
    local_r = math.sqrt(max(0.0, 1.0 - ny * ny))
    cos_p = math.cos(phase * 2 * math.pi)
    if phase <= 0.5:
        return nx - cos_p * local_r
    else:
        return -(nx + cos_p * local_r)


def _moon_colour(nx, ny, age, rotation=0.0):
    s, c = math.sin(rotation), math.cos(rotation)
    nx_r = nx * s - ny * c
    ny_r = nx * c + ny * s
    d = _terminator_d(nx_r, ny_r, age)
    blend = max(0.0, min(1.0, d * RADIUS / 1.5 + 0.5))
    tex = _load_texture()
    tx = max(0, min(SIZE - 1, round(nx * RADIUS + CX)))
    ty = max(0, min(SIZE - 1, round(ny * RADIUS + CY)))
    albedo = tex[tx, ty] / 255.0
    dark_scale = 0.28
    b = albedo * (dark_scale + blend * (1.0 - dark_scale))
    b = max(0.0, min(1.0, b))
    return (int(b * 215), int(b * 208), int(b * 195))


# ── Ring indicator ─────────────────────────────────────────────────────────────


def _perimeter():
    px = []
    for x in range(SIZE):
        px.append((x, 0))
        px.append((x, SIZE - 1))
    for y in range(1, SIZE - 1):
        px.append((0, y))
        px.append((SIZE - 1, y))
    return px


def _pixel_angle(x, y):
    return math.degrees(math.atan2(x - CX, -(y - CY))) % 360


def _arc_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _ring_colour(alt):
    horizon_dist = abs(alt)
    if horizon_dist < HORIZON_GLOW_DEG:
        t = horizon_dist / HORIZON_GLOW_DEG
        r = int(160 + t * (RING_ON[0] - 160))
        g = int(60 + t * (RING_ON[1] - 60))
        b = int(10 + t * (RING_ON[2] - 10))
        return (r, g, b)
    return RING_ON


# ── Event label ───────────────────────────────────────────────────────────────

_GLYPHS: dict[str, list[int]] = {
    "0": [0b111, 0b101, 0b101, 0b101, 0b111],
    "1": [0b010, 0b110, 0b010, 0b010, 0b111],
    "2": [0b111, 0b001, 0b111, 0b100, 0b111],
    "3": [0b111, 0b001, 0b011, 0b001, 0b111],
    "4": [0b101, 0b101, 0b111, 0b001, 0b001],
    "5": [0b111, 0b100, 0b111, 0b001, 0b111],
    "6": [0b111, 0b100, 0b111, 0b101, 0b111],
    "7": [0b111, 0b001, 0b001, 0b001, 0b001],
    "8": [0b111, 0b101, 0b111, 0b101, 0b111],
    "9": [0b111, 0b101, 0b111, 0b001, 0b111],
    "F": [0b111, 0b100, 0b110, 0b100, 0b100],
    # N: diagonal stroke avoids confusion with M
    "N": [0b101, 0b110, 0b101, 0b011, 0b101],
}


def _draw_label(pix, text: str, color: tuple[int, int, int]) -> None:
    """Write a tiny 3×5 pixel label in the bottom-left corner."""
    x0, y0 = 1, SIZE - 6
    cx = x0
    for ch in text:
        rows = _GLYPHS.get(ch)
        if rows is None:
            cx += 4
            continue
        for row_i, bits in enumerate(rows):
            for col_i in range(3):
                if bits & (1 << (2 - col_i)):
                    px, py = cx + col_i, y0 + row_i
                    if 0 <= px < SIZE and 0 <= py < SIZE:
                        pix[px, py] = color
        cx += 4


def _event_label(age: float) -> tuple[str, tuple[int, int, int]] | None:
    """Return (label_text, color) if within EVENT_LABEL_DAYS of an event, else None."""
    days_since_new = age % LUNAR_CYCLE
    days_to_full = (LUNAR_CYCLE / 2 - days_since_new) % LUNAR_CYCLE
    days_to_new = (LUNAR_CYCLE - days_since_new) % LUNAR_CYCLE
    if days_to_full < days_to_new:
        days = days_to_full
        prefix, color = "F", (255, 200, 50)   # gold
    else:
        days = days_to_new
        prefix, color = "N", (100, 180, 255)  # blue
    if days > EVENT_LABEL_DAYS:
        return None
    return f"{prefix}{round(days)}", color


# ── Public render function ─────────────────────────────────────────────────────


def render_image(lat: str, lon: str, elev: int) -> Image.Image:
    """Render a 64×64 moon phase image and return it as a PIL Image.

    This function is blocking (uses ephem) and must be called in an executor.
    """
    data = observe(lat, lon, elev)

    img = Image.new("RGB", (SIZE, SIZE), BG)
    pix = img.load()

    rotation = data["rotation"]
    ew = -1.0 if MIRROR_EW else 1.0
    for y in range(1, SIZE - 1):
        for x in range(1, SIZE - 1):
            dx, dy = x - CX, y - CY
            if dx * dx + dy * dy <= RADIUS * RADIUS:
                pix[x, y] = _moon_colour(ew * dx / RADIUS, dy / RADIUS, data["age"], ew * rotation)

    alt = data["alt"]
    ring_col = _ring_colour(alt)

    if alt > 0:
        MAX_ARC_PX = 10
        perimeter = _perimeter()
        n_perimeter = len(perimeter)
        arc_fraction = min(alt, data["peak_alt"]) / data["peak_alt"]
        arc_pixels = max(1, round(arc_fraction * MAX_ARC_PX))
        half_span = (arc_pixels / n_perimeter) * 360.0
        az = data["az"]
        if MIRROR_EW:
            az = (360.0 - az) % 360.0
        closest = min(perimeter, key=lambda p: _arc_diff(_pixel_angle(p[0], p[1]), az))
        for rx, ry in perimeter:
            if _arc_diff(_pixel_angle(rx, ry), az) <= half_span:
                pix[rx, ry] = ring_col
        pix[closest[0], closest[1]] = (120, 70, 30)
    else:
        fraction = data["rise_fraction"] or 0.0
        bar_height = max(1, round(fraction * SIZE))
        y_start = SIZE - bar_height
        for y in range(y_start, SIZE):
            pix[0, y] = ring_col
            pix[SIZE - 1, y] = ring_col

    label = _event_label(data["age"])
    if label is not None:
        _draw_label(pix, label[0], label[1])

    return img
