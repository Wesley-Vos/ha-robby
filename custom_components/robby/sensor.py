"""Robby Lawn Mower Entity for Home Assistant."""

from homeassistant.components.lawn_mower import LawnMowerActivity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import RobbyConfigEntry
from .const import CONF_POWER_SENSOR, CONF_SWITCH_SENSOR


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RobbyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor entity."""
    current_activity = RobbyActivitySensorEntity(hass, entry)
    async_add_entities([current_activity], update_before_add=True)


class RobbyActivitySensorEntity(SensorEntity):
    """Representation of a Robby sensor."""

    def __init__(self, hass: HomeAssistant, entry: RobbyConfigEntry) -> None:
        """Initialize the sensor entity."""
        self.hass = hass
        self._power_sensor = entry.data[CONF_POWER_SENSOR]
        self._switch_entity = entry.data[CONF_SWITCH_SENSOR]
        self._attr_name = "Robby current activity"
        self._attr_unique_id = (
            f"robby_current_activity_{self._power_sensor}_{self._switch_entity}"
        )
        self._power_val = 0
        self._switch_state = False
        self._stuck_state = False
        self._power_available = False
        self._switch_available = False
        self._stuck_available = False
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_translation_key = "activity"

        async_track_state_change_event(
            hass,
            [self._power_sensor, self._switch_entity, "switch.robby_stuck"],
            self._handle_state_change,
        )

    async def _handle_state_change(self, event):
        await self.async_update_ha_state(True)

    async def async_update_power(self):
        """Update the power state of the sensor."""
        if (power_state := self.hass.states.get(self._power_sensor)) is None:
            self._power_available = False
            return
        self._power_available = True
        try:
            self._power_val = float(power_state.state)
        except (ValueError, TypeError, AttributeError):
            self._power_val = -1

    async def async_update_switch(self):
        """Update the switch state of the sensor."""
        if (switch_state := self.hass.states.get(self._switch_entity)) is None:
            self._switch_available = False
            return
        self._switch_available = True
        self._switch_state = switch_state.state

    async def async_update_stuck(self):
        """Update the stuck state of the sensor."""
        if (robby_stuck_state := self.hass.states.get("switch.robby_stuck")) is None:
            self._stuck_available = False
            return
        self._stuck_available = True
        self._stuck_state = robby_stuck_state.state == STATE_ON

    async def async_update(self):
        """Update the state of the sensor based on power consumption."""
        await self.async_update_power()
        await self.async_update_switch()
        await self.async_update_stuck()

    @property
    def native_value(self) -> str:
        """Return the current activity of the sensor."""
        if self._power_val <= 0:
            return LawnMowerActivity.ERROR
        if self._power_val < 2:
            if self._stuck_state:
                return LawnMowerActivity.ERROR
            return LawnMowerActivity.MOWING
        if 2 <= self._power_val < 3:
            return LawnMowerActivity.DOCKED
        return "charging"

    @property
    def available(self) -> bool:
        """Return availability of sensor."""
        return (
            self._power_available
            and self._switch_available
            and self._stuck_available
            and self._switch_state == STATE_ON
        )

    @property
    def options(self) -> list[str]:
        """Return the options of the sensor."""
        return [
            LawnMowerActivity.MOWING,
            LawnMowerActivity.DOCKED,
            LawnMowerActivity.ERROR,
            "charging",
        ]
