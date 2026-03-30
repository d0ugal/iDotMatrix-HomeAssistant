# iDotMatrix Home Assistant Integration

A focused Home Assistant integration for **iDotMatrix** pixel art displays, built around
automation-driven image display. Connects directly to your device via Bluetooth (native
adapter or ESPHome proxy) with no cloud dependencies.

---

## Features

- **Moon phase display** — renders a real-time moon phase image using your HA home location
- **Now playing** — shows album art with scrolling track/artist overlay from any HA media player
- **Display any image** — send a PNG, JPG, or animated GIF; automatically centre-cropped and resized to 64×64
- **Automation-friendly** — all display modes are triggered by service calls; schedule and combine them however you like
- **Temporary displays** — `display_for` reverts back to the previous default after a set number of seconds
- **Persistent default** — the last permanent display call is saved to disk and replayed on HA restart and device power-cycle
- **Light entity** — turn the screen on/off and adjust brightness; turning on replays the current default

---

## Installation

Copy `custom_components/idotmatrix/` into your HA `config/custom_components/` directory
and restart Home Assistant. The device will be discovered automatically via Bluetooth if
nearby, or you can add it manually via **Settings → Integrations → Add Integration → iDotMatrix**.

---

## Services

### `idotmatrix.display_moon`

Renders the current moon phase (using your HA home lat/lon/elevation) and uploads it to
the display. Becomes the new default.

```yaml
action: idotmatrix.display_moon
```

### `idotmatrix.display_now_playing`

Fetches album art from a media player entity, overlays scrolling track and artist text,
and uploads as an animated GIF. Becomes the new default. GIFs are cached on disk by
content hash — repeat plays are instant.

```yaml
action: idotmatrix.display_now_playing
data:
  entity_id: media_player.living_room_speaker
```

### `idotmatrix.display_image`

Uploads any image or animated GIF. The image is automatically centre-cropped to square
and resized to 64×64. Becomes the new default unless `display_for` is set.

```yaml
action: idotmatrix.display_image
data:
  path: /config/www/doorbell.gif
  display_for: 15   # optional — reverts to previous default after 15 seconds
```

All three services accept an optional `display_for` (seconds). When set, the call is
**temporary** — it displays for that duration then automatically reverts to whichever
display was set before. Without `display_for`, the call updates the persisted default.

---

## Entities

| Entity | Type | Notes |
|---|---|---|
| `light.idotmatrix` | Light | On/off + brightness. Attributes show current display info. |
| `sensor.idotmatrix_ble_connected` | Sensor | `connected` / `disconnected` |
| `sensor.idotmatrix_last_updated` | Sensor | Timestamp of last successful upload |

Turning `light.idotmatrix` **on** calls `screenOn()` and replays the current default display.

---

## Example automations

**Moon phase — refresh every 5 minutes**
```yaml
automation:
  - alias: iDotMatrix Moon Refresh
    trigger:
      - platform: homeassistant
        event: start
      - platform: time_pattern
        minutes: "/5"
    condition:
      - condition: template
        value_template: >
          {{ state_attr('light.idotmatrix', 'display_mode') in ['moon', None] }}
    action:
      - action: idotmatrix.display_moon
```

**Now playing — show art when track changes, revert to moon when stopped**
```yaml
automation:
  - alias: iDotMatrix Now Playing
    trigger:
      - platform: state
        entity_id: media_player.extension_speaker
        to: "playing"
      - platform: state
        entity_id: media_player.extension_speaker
        attribute: media_title
    condition:
      - condition: state
        entity_id: media_player.extension_speaker
        state: "playing"
    action:
      - action: idotmatrix.display_now_playing
        data:
          entity_id: media_player.extension_speaker

  - alias: iDotMatrix Music Stopped
    trigger:
      - platform: state
        entity_id: media_player.extension_speaker
        not_to: "playing"
    action:
      - action: idotmatrix.display_moon
```

**Doorbell — show animation then return to whatever was showing**
```yaml
automation:
  - alias: iDotMatrix Doorbell
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_doorbell
        to: "on"
    action:
      - action: idotmatrix.display_image
        data:
          path: /config/www/doorbell.gif
          display_for: 15
```

**Screen on/off**
```yaml
automation:
  - alias: iDotMatrix Screen Off
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - action: light.turn_off
        target:
          entity_id: light.idotmatrix

  - alias: iDotMatrix Screen On
    trigger:
      - platform: state
        entity_id: input_boolean.is_somebody_up
        to: "on"
    action:
      - action: light.turn_on
        target:
          entity_id: light.idotmatrix
```

---

## Credits

This integration is a fork of
[tukies/iDotMatrix-HomeAssistant](https://github.com/tukies/iDotMatrix-HomeAssistant)
(MIT licence). The original project provided the Bluetooth client library and initial
integration scaffolding. This fork has been substantially rewritten — the display
architecture, service API, and entity model are entirely new — but the underlying BLE
protocol work from the original authors is preserved and credited.

The moon phase renderer is based on astronomical calculations using the
[ephem](https://pypi.org/project/ephem/) library.

The pixel-font text overlay is ported from
[tomglenn/idx-ai](https://github.com/tomglenn/idx-ai) (MIT licence).
