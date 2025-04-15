"""The Robby integration."""

from __future__ import annotations

from homeassistant.components.lawn_mower import LawnMowerActivity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    Platform,
)
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.dt import now

from .const import STATE_CHARGING

_PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.DATETIME,
    Platform.LAWN_MOWER,
    Platform.SWITCH,
]

_ROBBY_START_CHARGING_CYCLE_ENTITY_ID = "datetime.robby_start_charging_cycle"
_ROBBY_END_CHARGING_CYCLE_ENTITY_ID = "datetime.robby_end_charging_cycle"
_ROBBY_START_MOWING_CYCLE_ENTITY_ID = "datetime.robby_start_mowing_cycle"
_ROBBY_END_MOWING_CYCLE_ENTITY_ID = "datetime.robby_end_mowing_cycle"
_ROBBY_SWITCH_STUCK_ENTITY_ID = "switch.robby_stuck"

type RobbyConfigEntry = ConfigEntry  # noqa: F821


async def async_setup_entry(hass: HomeAssistant, entry: RobbyConfigEntry) -> bool:
    """Set up Robby from a config entry."""

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    """Actions"""

    # def is_mowing() -> bool:
    #     """Check if the Robby is mowing according to dts."""
    #     start_dt = parse_datetime(
    #         hass.states.get(_ROBBY_START_MOWING_CYCLE_ENTITY_ID).state
    #     )
    #     stop_dt = parse_datetime(
    #         hass.states.get(_ROBBY_STOP_MOWING_CYCLE_ENTITY_ID).state
    #     )

    #     return start_dt > stop_dt

    # def is_charging() -> bool:
    #     """Check if the Robby is charging according to dts."""
    #     start_dt = parse_datetime(
    #         hass.states.get(_ROBBY_START_CHARGING_CYCLE_ENTITY_ID).state
    #     )
    #     stop_dt = parse_datetime(
    #         hass.states.get(_ROBBY_STOP_CHARGING_CYCLE_ENTITY_ID).state
    #     )

    #     return start_dt > stop_dt

    async def start_charging() -> None:
        """Start charging the Robby."""
        await hass.services.async_call(
            "datetime",
            "set_value",
            {
                ATTR_ENTITY_ID: _ROBBY_START_CHARGING_CYCLE_ENTITY_ID,
                "datetime": now().isoformat(),
            },
            blocking=False,
        )

    async def stop_charging() -> None:
        """Stop charging the Robby."""
        await hass.services.async_call(
            "datetime",
            "set_value",
            {
                ATTR_ENTITY_ID: _ROBBY_END_CHARGING_CYCLE_ENTITY_ID,
                "datetime": now().isoformat(),
            },
            blocking=False,
        )

    async def start_mowing() -> None:
        """Start mowing with the Robby."""
        await hass.services.async_call(
            "datetime",
            "set_value",
            {
                ATTR_ENTITY_ID: _ROBBY_START_MOWING_CYCLE_ENTITY_ID,
                "datetime": now().isoformat(),
            },
            blocking=False,
        )

    async def stop_mowing() -> None:
        """Stop mowing with the Robby."""
        await hass.services.async_call(
            "datetime",
            "set_value",
            {
                ATTR_ENTITY_ID: _ROBBY_END_MOWING_CYCLE_ENTITY_ID,
                "datetime": now().isoformat(),
            },
            blocking=False,
        )

    async def getting_stuck() -> None:
        """Handle the Robby getting stuck."""
        await hass.services.async_call(
            "homeassistant",
            "turn_on",
            {"entity_id": _ROBBY_SWITCH_STUCK_ENTITY_ID},
            blocking=False,
        )

    async def released() -> None:
        """Handle the Robby being released."""
        await hass.services.async_call(
            "homeassistant",
            "turn_off",
            {"entity_id": _ROBBY_SWITCH_STUCK_ENTITY_ID},
            blocking=False,
        )

    async def async_handle_state_change(
        event: Event[EventStateChangedData],
    ) -> None:
        """Process state change event."""
        data = event.data
        old_state = (
            data.get("old_state").state if data.get("old_state") is not None else None
        )
        new_state = (
            data.get("new_state").state if data.get("new_state") is not None else None
        )

        print("Transition from", old_state, "to", new_state)

        if old_state == new_state:
            return

        if old_state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or new_state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            # Handle unavailable or unknown state
            return

        # Handle other state changes
        if old_state == LawnMowerActivity.DOCKED:
            if new_state == LawnMowerActivity.MOWING:
                print("Started mowing after being dokced")
                await start_mowing()
            elif new_state == STATE_CHARGING:
                print("Started charging")
                await start_charging()
        elif old_state == STATE_CHARGING:
            await stop_charging()
            if new_state == LawnMowerActivity.MOWING:
                await start_mowing()
                print("Finished charging and started mowing")
            if new_state == LawnMowerActivity.DOCKED:
                print("Finished charging")
        elif old_state in (LawnMowerActivity.MOWING, LawnMowerActivity.ERROR):
            if new_state == LawnMowerActivity.DOCKED:
                print("Finished mowing and returned to dock without charging")
                await stop_mowing()
                await released()
            elif new_state == STATE_CHARGING:
                print("Finished mowing, returned to dock and started charging")
                await stop_mowing()
                await released()
                await start_charging()

    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            "lawn_mower.robby",
            async_handle_state_change,
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: RobbyConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
