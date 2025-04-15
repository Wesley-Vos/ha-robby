"""Robby Lawn Mower Entity for Home Assistant."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import RobbyConfigEntry
from .const import CONF_POWER_SENSOR, CONF_SWITCH_SENSOR
from .device_binding import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RobbyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the binary sensor entity."""
    charging = RobbyChargingBinarySensorEntity(hass, entry)
    async_add_entities([charging], update_before_add=True)


class RobbyChargingBinarySensorEntity(BinarySensorEntity):
    """Representation of a Robby charging binary sensor."""

    def __init__(self, hass: HomeAssistant, entry: RobbyConfigEntry) -> None:
        """Initialize the charging binary sensor entity."""
        self.hass = hass
        self._power_sensor = entry.data[CONF_POWER_SENSOR]
        self._switch_entity = entry.data[CONF_SWITCH_SENSOR]
        self._attr_name = "Robby charging"
        self._attr_unique_id = (
            f"robby_charging_binary_sensor_{self._power_sensor}_{self._switch_entity}"
        )
        self._power_val = 0
        self._switch_state = False
        self._stuck_state = False
        self._power_available = False
        self._switch_available = False
        self._attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
        self.device_info = get_device_info(hass, entry)

        async_track_state_change_event(
            hass,
            [self._power_sensor, self._switch_entity],
            self._handle_state_change,
        )

    async def _handle_state_change(self, event):
        await self.async_update_ha_state(True)

    async def async_update_power(self):
        """Update the power state of the binary sensor."""
        if (power_state := self.hass.states.get(self._power_sensor)) is None:
            self._power_available = False
            return
        self._power_available = True
        try:
            self._power_val = float(power_state.state)
        except (ValueError, TypeError, AttributeError):
            self._power_val = -1

    async def async_update_switch(self):
        """Update the switch state of the binary sensor."""
        if (switch_state := self.hass.states.get(self._switch_entity)) is None:
            self._switch_available = False
            return
        self._switch_available = True
        self._switch_state = switch_state.state

    async def async_update(self):
        """Update the state of the binary sensor based on power consumption."""
        await self.async_update_power()
        await self.async_update_switch()

    @property
    def is_on(self) -> bool | None:
        """Return the current state of the binary sensor."""
        return self._power_val >= 3

    @property
    def available(self) -> bool:
        """Return availability of binary sensor."""
        return (
            self._power_available
            and self._switch_available
            and self._switch_state == STATE_ON
        )
