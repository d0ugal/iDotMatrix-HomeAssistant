"""Config flow for iDotMatrix integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_MAC, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iDotMatrix."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            address = user_input[CONF_MAC]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, DEFAULT_NAME),
                data={
                    CONF_MAC: address,
                    CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME),
                },
            )

        from homeassistant.components import bluetooth

        discovered = {
            info.address: f"{info.name} ({info.address})"
            for info in bluetooth.async_discovered_service_info(self.hass)
            if info.name and info.name.startswith("IDM-")
        }

        schema = vol.Schema(
            {
                vol.Required(CONF_MAC): (
                    vol.In(list(discovered.keys())) if discovered else str
                ),
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self.discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm bluetooth discovery."""
        if user_input is not None:
            name = self.discovery_info.name or DEFAULT_NAME
            return self.async_create_entry(
                title=name,
                data={CONF_MAC: self.discovery_info.address, CONF_NAME: name},
            )
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self.discovery_info.name},
        )
