"""Robby Lawn Mower Entity for Home Assistant."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import RobbyConfigEntry
from .const import CONF_POWER_SENSOR, CONF_SWITCH_SENSOR


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RobbyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the lawn mower entity."""
    stuck_switch = RobbyStuckSwitchEntity(hass, entry)
    async_add_entities([stuck_switch], update_before_add=True)


class RobbyStuckSwitchEntity(SwitchEntity, RestoreEntity):
    """Representation of a Robby stuck switch."""

    def __init__(self, hass: HomeAssistant, entry: RobbyConfigEntry) -> None:
        """Initialize the lawn mower entity."""
        self.hass = hass
        self.entry = entry
        self._power_sensor = entry.data[CONF_POWER_SENSOR]
        self._switch_entity = entry.data[CONF_SWITCH_SENSOR]
        self._attr_name = "Robby stuck"
        self._attr_unique_id = (
            f"robby_stuck_switch_{self._power_sensor}_{self._switch_entity}"
        )
        self._state = None

    @property
    def state(self):
        """Return the state of the switch."""
        return self._state

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if not state:
            self._state = STATE_OFF
        else:
            self._state = state.state

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        self._state = STATE_ON
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        self._state = STATE_OFF
        self.async_write_ha_state()
