"""GitHub sensor platform."""
from __future__ import annotations

from datetime import date, timedelta
import logging
import async_timeout
import voluptuous as vol

from .manchester_council_api import ManchesterCouncilApi
from .const import DEVICE_CLASS, DOMAIN, CONF_ADDRESS, CONF_POSTCODE, STATE_ATTR_COLOUR, STATE_ATTR_DAYS, STATE_ATTR_NEXT_COLLECTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
import homeassistant.util.dt as dt_util

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_POSTCODE): cv.string,
        vol.Required(CONF_ADDRESS): cv.string,
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    if discovery_info is None:
        return

    api = ManchesterCouncilApi(discovery_info.get(CONF_POSTCODE), discovery_info.get(CONF_ADDRESS))
    coordinator = HouseholdBinCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
      BinSensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )

class HouseholdBinCoordinator(DataUpdateCoordinator):
  """Household Bin Coordinator"""

  def __init__(self, hass, api):
    """Initialize my coordinator."""
    super().__init__(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="My sensor",
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )
    self.api = api

  async def _async_update_data(self):
    async with async_timeout.timeout(10):
      data = await self.hass.async_add_executor_job(
          self.api.fetch_data
      )

    return data

class BinSensor(CoordinatorEntity, SensorEntity):
    """Representation of a bin sensor."""

    device_class = DEVICE_CLASS

    def __init__(self, coordinator, idx):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.idx = idx
        self.apply_values()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.apply_values()
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sun."""
        return {
            STATE_ATTR_COLOUR: self._colour,
            STATE_ATTR_NEXT_COLLECTION: self._next_collection,
            STATE_ATTR_DAYS: self._days,
        }

    def apply_values(self):
      self._id = self.coordinator.data[self.idx]["id"]
      self._colour = self.coordinator.data[self.idx]["colour"]
      self._name = f"{self._colour} bin"
      self._next_collection = self.coordinator.data[self.idx]["next_collection"].isoformat()
      self._hidden = False
      self._icon = "mdi:trash-can"
      self._state = "unknown"

      now = dt_util.now()
      next_collection = self.coordinator.data[self.idx]["next_collection"]
      this_week_start = now.date() - timedelta(days=now.weekday())
      this_week_end = this_week_start + timedelta(days=6)
      next_week_start = this_week_end + timedelta(days=1)
      next_week_end = next_week_start + timedelta(days=6)

      self._days = (next_collection - now.date()).days

      if next_collection == now.date():
        self._state = "today"
      elif next_collection == (now + timedelta(days=1)).date():
        self._state = "tomorrow"
      elif next_collection >= this_week_start and next_collection <= this_week_end:
        self._state = "this_week"
      elif next_collection >= next_week_start and next_collection <= next_week_end:
        self._state = "next_week"
      elif next_collection > next_week_end:
        self._state = "future"
      else:
        self._state = "unknown"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def hidden(self):
        """Return the hidden attribute."""
        return self._hidden

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def days(self):
        """Return the days of the sensor."""
        return self._days

    @property
    def next_collection(self):
        """Return the next collection of the sensor."""
        return self._next_collection

    @property
    def colour(self):
        """Return the colour of the sensor."""
        return self._colour

    @property
    def icon(self):
        """Return the entity icon."""
        return self._icon

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self._id
        # return self.config.get("unique_id", None)

