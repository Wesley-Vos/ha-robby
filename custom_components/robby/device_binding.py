from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from . import RobbyConfigEntry
from .const import CONF_POWER_SENSOR, DOMAIN


def get_device_info(hass: HomeAssistant, entry: RobbyConfigEntry) -> DeviceInfo:
    """Get device info for a given sensor."""

    return DeviceInfo(
        name=DOMAIN[0].upper() + DOMAIN[1:],
        identifiers={(DOMAIN, entry.data[CONF_POWER_SENSOR])},
        model="Robby",
        manufacturer="Parkside",
    )
