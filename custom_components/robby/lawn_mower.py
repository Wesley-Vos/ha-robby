"""Robby Lawn Mower Entity for Home Assistant."""

from homeassistant.components.lawn_mower import (
    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import RobbyConfigEntry
from .const import ATTR_CHARGING, CONF_POWER_SENSOR, CONF_SWITCH_SENSOR


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RobbyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the lawn mower entity."""
    mower = RobbyLawnMowerEntity(hass, entry)
    async_add_entities([mower], update_before_add=True)


class RobbyLawnMowerEntity(LawnMowerEntity):
    """Representation of a Robby lawn mower."""

    def __init__(self, hass: HomeAssistant, entry: RobbyConfigEntry) -> None:
        """Initialize the lawn mower entity."""
        self.hass = hass
        self._power_sensor = entry.data[CONF_POWER_SENSOR]
        self._switch_entity = entry.data[CONF_SWITCH_SENSOR]
        self._attr_name = "Robby"
        self._attr_unique_id = (
            f"robby_lawn_mower_{self._power_sensor}_{self._switch_entity}"
        )
        self._power_val = 0
        self._switch_state = False
        self._stuck_state = False
        self._power_available = False
        self._switch_available = False
        self._stuck_available = False
        self._attr_supported_features = LawnMowerEntityFeature.PAUSE

        async_track_state_change_event(
            hass,
            [self._power_sensor, self._switch_entity, "switch.robby_stuck"],
            self._handle_state_change,
        )

    async def _handle_state_change(self, event):
        await self.async_update_ha_state(True)

    async def async_update_power(self):
        """Update the power state of the lawn mower."""
        if (power_state := self.hass.states.get(self._power_sensor)) is None:
            self._power_available = False
            return
        self._power_available = True
        try:
            self._power_val = float(power_state.state)
        except (ValueError, TypeError, AttributeError):
            self._power_val = -1

    async def async_update_switch(self):
        """Update the switch state of the lawn mower."""
        if (switch_state := self.hass.states.get(self._switch_entity)) is None:
            self._switch_available = False
            return
        self._switch_available = True
        self._switch_state = switch_state.state

    async def async_update_stuck(self):
        """Update the stuck state of the lawn mower."""
        if (robby_stuck_state := self.hass.states.get("switch.robby_stuck")) is None:
            self._stuck_available = False
            return
        self._stuck_available = True
        self._stuck_state = robby_stuck_state.state == STATE_ON

    async def async_update(self):
        """Update the state of the lawn mower based on power consumption."""
        await self.async_update_power()
        await self.async_update_switch()
        await self.async_update_stuck()

    @property
    def activity(self) -> LawnMowerActivity:
        """Return the current activity of the lawn mower."""
        if self._power_val <= 0 or self._stuck_state:
            return LawnMowerActivity.ERROR
        if self._power_val < 2:
            return LawnMowerActivity.MOWING
        return LawnMowerActivity.DOCKED

    @property
    def available(self) -> bool:
        """Return availability of lawn mower."""
        return (
            self._power_available
            and self._switch_available
            and self._stuck_available
            and self._switch_state == STATE_ON
        )

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the lawn mower."""
        return {ATTR_CHARGING: self._power_val >= 3}

    async def async_pause(self) -> None:
        """Pause the lawn mower."""
        await self.hass.services.async_call(
            "homeassistant",
            "turn_off",
            {"entity_id": self._switch_entity},
            blocking=True,
        )
        self.async_write_ha_state()
