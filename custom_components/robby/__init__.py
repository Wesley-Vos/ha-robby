"""The Robby integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.LAWN_MOWER,
    Platform.SWITCH,
]

type RobbyConfigEntry = ConfigEntry[RobbyData]  # noqa: F821


@dataclass
class RobbyData:
    """Data for Robby."""

    is_stuck: bool


async def async_setup_entry(hass: HomeAssistant, entry: RobbyConfigEntry) -> bool:
    """Set up Robby from a config entry."""

    entry.runtime_data = RobbyData(is_stuck=False)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: RobbyConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
