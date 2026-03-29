# iDotMatrix Moon Display Debugging

## Architecture

```
HA coordinator (moon.py)
    → renders 64×64 PIL image every 5 minutes
        → uploads via BLE ESPHome proxy → iDotMatrix 64×64 display
```

Display mode is set to **Moon Phase** via the iDotMatrix display mode select entity in HA.
Location is taken from HA's configured home location (Settings → System → General).

## Quick checks

### Is the coordinator rendering?
```
grep "Moon image rendered\|Failed to render moon" /config/home-assistant.log | tail -10
```
Expected: `Moon image rendered and uploaded` every 5 minutes.

### Is the BLE device connected?
```
grep "IDM-03D68A\|idotmatrix" /config/home-assistant.log | tail -10
```
Expected: `connected to 36:88:17:03:D6:8A` on first render after HA restart.

### Force an immediate re-render
Call from HA Developer Tools → Services:
```yaml
service: idotmatrix.refresh
```

### Send a raw image manually
```yaml
service: idotmatrix.send_image
data:
  image_path: /share/some/image.png
```
Note: this sets display mode to `external` — call `idotmatrix.refresh` or switch back
to Moon Phase to resume normal rendering.

---

## How the display protocol works

The device has two distinct upload modes with very different persistence behaviour:

**Raw image** (`setMode(1)` + raw RGB data)
Puts the device into a DIY drawing mode. The image lives in a volatile buffer tied
to the active BLE session. When BLE disconnects, the device exits that mode and the
display goes blank. This is why repeatedly re-uploading every 30 seconds was needed
as a workaround — the image had to be re-sent before the ESPHome proxy timed out
the connection (~55 seconds of inactivity).

**GIF upload**
The device has an internal GIF cache indexed by CRC32. Uploaded GIFs are stored
persistently and replayed from device memory — BLE does not need to stay connected.
This is also why the built-in clock mode survives disconnects; it is a native device
mode running independently of BLE.

**Conclusion:** Always upload as a single-frame GIF for any static image that needs
to persist. The moon renderer now does this, which is why a 5-minute refresh interval
is sufficient.

---

## Common failure modes

### Display goes blank after HA restart
The coordinator renders on a 5-minute timer. It does not push immediately on startup.
**Fix:** Call `idotmatrix.refresh` from Developer Tools, or wait up to 5 minutes.

### Display blank, no "Moon image rendered" log
Check for errors:
```
grep "Failed to render moon\|send_image\|not connected" /config/home-assistant.log | tail -10
```

### `could not enter image mode due to Interrupted by interrupt context manager`
Not a real error — appears when a previous upload is interrupted mid-way. The next
render (within 5 minutes) will complete cleanly.

### Display shows old image / stops updating
Reload the iDotMatrix integration from HA → Settings → Integrations.

---

## Key entities / IDs

| Thing | Value |
|---|---|
| Device MAC | `36:88:17:03:D6:8A` |
| Device name | `IDM-03D68A` |
| BLE proxy | `esp32-bluetooth-proxy-d4edf4` |
| Display mode entity | `select.idotmatrix_display_mode` |

---

## Config knobs (moon.py)

| Constant | Purpose |
|---|---|
| `MIRROR_EW` | `True` = north-facing wall (flips east↔west) |
| `dark_scale` | Brightness of dark side (earthshine); 0=black, 1=same as lit |
| `MAX_ARC_PX` | Max pixels in the direction arc (currently 10) |
| `HORIZON_GLOW_DEG` | Degrees from horizon where ring warms to orange |
