"""Sensors for iDotMatrix."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_MAC
from .coordinator import IDotMatrixCoordinator
from .entity import IDotMatrixEntity
from .client.connectionManager import ConnectionManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: IDotMatrixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        IDotMatrixBLESensor(coordinator, entry),
        IDotMatrixScreenSensor(coordinator, entry),
        IDotMatrixLastRenderSensor(coordinator, entry),
    ])


class IDotMatrixBLESensor(IDotMatrixEntity, SensorEntity):
    """BLE connection status."""

    _attr_name = "BLE Connected"
    _attr_icon = "mdi:bluetooth"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_MAC]}_ble_connected"

    @property
    def native_value(self) -> str:
        conn = ConnectionManager()
        if conn and conn.client and conn.client.is_connected:
            return "connected"
        return "disconnected"


class IDotMatrixScreenSensor(IDotMatrixEntity, SensorEntity):
    """Whether the display is on or off."""

    _attr_name = "Screen"
    _attr_icon = "mdi:monitor"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_MAC]}_screen"

    @property
    def native_value(self) -> str:
        return "on" if self.coordinator.screen_on else "off"


class IDotMatrixLastRenderSensor(IDotMatrixEntity, SensorEntity):
    """Timestamp of the last successful moon render."""

    _attr_name = "Last Render"
    _attr_icon = "mdi:clock-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.data[CONF_MAC]}_last_render"

    @property
    def native_value(self):
        ts = self.coordinator.last_render_time
        if ts is None:
            return None
        from homeassistant.util import dt as dt_util
        return dt_util.parse_datetime(ts)
