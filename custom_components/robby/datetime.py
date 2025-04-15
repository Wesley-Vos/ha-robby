"""Robby Lawn Mower Entity for Home Assistant."""

from datetime import datetime

from homeassistant.components.datetime import DateTimeEntity, DateTimeEntityDescription
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import RobbyConfigEntry
from .const import CONF_POWER_SENSOR, CONF_SWITCH_SENSOR
from .device_binding import get_device_info

ENTITIES: tuple[DateTimeEntityDescription, ...] = (
    DateTimeEntityDescription(
        key="robby_start_mowing_cycle",
        name="Robby start mowing cycle",
        icon="mdi:clock-start",
    ),
    DateTimeEntityDescription(
        key="robby_end_mowing_cycle",
        name="Robby end mowing cycle",
        icon="mdi:clock-end",
    ),
    DateTimeEntityDescription(
        key="robby_start_charging_cycle",
        name="Robby start charging cycle",
        icon="mdi:clock-start",
    ),
    DateTimeEntityDescription(
        key="robby_end_charging_cycle",
        name="Robby end charging cycle",
        icon="mdi:clock-end",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RobbyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the datetime entities."""
    entities: list = [
        RobbyDateTimeEntity(hass, entry, description) for description in ENTITIES
    ]
    async_add_entities(entities, update_before_add=True)


class RobbyDateTimeEntity(DateTimeEntity, RestoreEntity):
    """Representation of a Robby datetime entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: RobbyConfigEntry,
        description: DateTimeEntityDescription,
    ) -> None:
        """Initialize the datetime entity."""
        self.hass = hass
        self.entry = entry
        self._power_sensor = entry.data[CONF_POWER_SENSOR]
        self._switch_entity = entry.data[CONF_SWITCH_SENSOR]
        self._attr_name = description.name
        self._attr_unique_id = (
            f"{description.key}_{self._power_sensor}_{self._switch_entity}"
        )
        self._state: datetime | None = None
        self.device_info = get_device_info(hass, entry)

    @property
    def native_value(self):
        """Return the state of the datetime."""
        return self._state

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if not state or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._state = None
        else:
            self._state = datetime.fromisoformat(state.state)

    async def async_set_value(self, value: datetime) -> None:
        """Update the current value."""
        self._state = value
        self.async_write_ha_state()
