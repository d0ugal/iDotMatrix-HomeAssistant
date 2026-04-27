"""Light platform for iDotMatrix — screen power and brightness."""

from __future__ import annotations

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MAC, DOMAIN
from .coordinator import IDotMatrixCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: IDotMatrixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IDotMatrixLight(coordinator, entry)])


class IDotMatrixLight(CoordinatorEntity[IDotMatrixCoordinator], LightEntity):
    """The iDotMatrix display as a light entity.

    on/off controls the screen; brightness maps HA 0-255 → device 5-100%.
    Turning on replays the current default display.
    extra_state_attributes exposes what is currently shown.
    """

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_has_entity_name = True
    _attr_name = None  # use the device name as the entity name

    def __init__(self, coordinator: IDotMatrixCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        mac = entry.data[CONF_MAC]
        self._attr_unique_id = mac
        self._attr_device_info = {
            "identifiers": {(DOMAIN, mac)},
            "name": entry.title,
            "manufacturer": "iDotMatrix",
        }

    @property
    def is_on(self) -> bool:
        return self.coordinator.screen_on

    @property
    def brightness(self) -> int:
        return self.coordinator.brightness

    @property
    def extra_state_attributes(self) -> dict:
        attrs: dict = {}
        if self.coordinator.display_mode:
            attrs["display_mode"] = self.coordinator.display_mode
        attrs.update(self.coordinator.display_attrs)
        return attrs

    async def async_turn_on(self, **kwargs) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        was_off = not self.coordinator.screen_on

        if was_off:
            await self.coordinator.do_screen_on()

        if brightness is not None:
            await self.coordinator.do_set_brightness(brightness)

        # Replay when turning on (was off, or explicit turn_on with no other args)
        if was_off or not kwargs:
            await self.coordinator._replay_default()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.do_screen_off()
