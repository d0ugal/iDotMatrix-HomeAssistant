"""The iDotMatrix integration."""
from __future__ import annotations

import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_MAC, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_SCHEMA_DISPLAY_MOON = vol.Schema({
    vol.Optional("display_for"): vol.Coerce(float),
})
_SCHEMA_DISPLAY_NOW_PLAYING = vol.Schema({
    vol.Required("entity_id"): cv.entity_id,
    vol.Optional("display_for"): vol.Coerce(float),
})
_SCHEMA_DISPLAY_IMAGE = vol.Schema({
    vol.Required("path"): cv.string,
    vol.Optional("display_for"): vol.Coerce(float),
})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .coordinator import IDotMatrixCoordinator
    from .client.connectionManager import ConnectionManager

    hass.data.setdefault(DOMAIN, {})

    manager = ConnectionManager()
    manager.set_hass(hass)
    manager.address = entry.data[CONF_MAC]

    coordinator = IDotMatrixCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_load_and_replay()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Services iterate all loaded coordinators so they work if multiple devices
    # are ever added.
    def _coordinators():
        return [
            c for c in hass.data.get(DOMAIN, {}).values()
            if isinstance(c, IDotMatrixCoordinator)
        ]

    async def _display_moon(call) -> None:
        display_for = call.data.get("display_for")
        for coord in _coordinators():
            await coord.do_display_moon(display_for=display_for)

    async def _display_now_playing(call) -> None:
        display_for = call.data.get("display_for")
        for coord in _coordinators():
            await coord.do_display_now_playing(
                call.data["entity_id"], display_for=display_for
            )

    async def _display_image(call) -> None:
        display_for = call.data.get("display_for")
        for coord in _coordinators():
            await coord.do_display_image(call.data["path"], display_for=display_for)

    if not hass.services.has_service(DOMAIN, "display_moon"):
        hass.services.async_register(DOMAIN, "display_moon", _display_moon, _SCHEMA_DISPLAY_MOON)
        hass.services.async_register(DOMAIN, "display_now_playing", _display_now_playing, _SCHEMA_DISPLAY_NOW_PLAYING)
        hass.services.async_register(DOMAIN, "display_image", _display_image, _SCHEMA_DISPLAY_IMAGE)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from .coordinator import IDotMatrixCoordinator

    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator:
        coordinator.cancel_revert()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    # Remove services only when the last entry is gone
    if not any(
        isinstance(c, IDotMatrixCoordinator)
        for c in hass.data.get(DOMAIN, {}).values()
    ):
        for svc in ("display_moon", "display_now_playing", "display_image"):
            hass.services.async_remove(DOMAIN, svc)

    return unload_ok
