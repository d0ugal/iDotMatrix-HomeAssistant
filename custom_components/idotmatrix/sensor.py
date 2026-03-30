"""Sensor platform for iDotMatrix — BLE connectivity and last updated timestamp."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_MAC, DOMAIN
from .coordinator import IDotMatrixCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: IDotMatrixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            IDotMatrixBLESensor(coordinator, entry),
            IDotMatrixLastUpdatedSensor(coordinator, entry),
        ]
    )


class _IDotMatrixSensorBase(CoordinatorEntity[IDotMatrixCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: IDotMatrixCoordinator, entry: ConfigEntry, key: str) -> None:
        super().__init__(coordinator)
        mac = entry.data[CONF_MAC]
        self._attr_unique_id = f"{mac}_{key}"
        self._attr_device_info = {"identifiers": {(DOMAIN, mac)}}


class IDotMatrixBLESensor(_IDotMatrixSensorBase):
    """Shows whether the BLE link to the device is currently active."""

    _attr_device_class = SensorDeviceClass.CONNECTIVITY
    _attr_name = "BLE Connected"

    def __init__(self, coordinator: IDotMatrixCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "ble_connected")

    @property
    def native_value(self) -> str:
        connected = (self.coordinator.data or {}).get("connected", False)
        return "connected" if connected else "disconnected"


class IDotMatrixLastUpdatedSensor(_IDotMatrixSensorBase):
    """Timestamp of the last successful image upload to the display."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_name = "Last Updated"

    def __init__(self, coordinator: IDotMatrixCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_updated")

    @property
    def native_value(self):
        if self.coordinator.last_updated:
            return dt_util.parse_datetime(self.coordinator.last_updated)
        return None
