"""Config flow for the Robby integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.input_boolean import DOMAIN as INPUT_BOOLEAN_DOMAIN
from homeassistant.components.input_number import DOMAIN as INPUT_NUMBER_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import CONF_POWER_SENSOR, CONF_SWITCH_SENSOR, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_POWER_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=[INPUT_NUMBER_DOMAIN, SENSOR_DOMAIN]),
        ),
        vol.Required(CONF_SWITCH_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=[INPUT_BOOLEAN_DOMAIN, SWITCH_DOMAIN]),
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    return {
        "title": "Robby",
        "power_sensor_entity_id": data[CONF_POWER_SENSOR],
        "switch_sensor_entity_id": data[CONF_SWITCH_SENSOR],
    }


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Robby."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            info = await validate_input(self.hass, user_input)
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
