"""Bin Collection Manchester Council Component."""

import voluptuous as vol

from homeassistant import helpers, core
from homeassistant.const import Platform
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv

from .const import CONF_ADDRESS, CONF_POSTCODE, DOMAIN

CONFIG_SCHEMA = vol.Schema({
      DOMAIN: vol.Schema({
        vol.Required(CONF_POSTCODE): cv.string,
        vol.Required(CONF_ADDRESS): cv.string,
    })
  },
  extra=vol.ALLOW_EXTRA
)

async def async_setup(
    hass: core.HomeAssistant, config: helpers.typing.ConfigType
) -> bool:
    """Set up the Bin Collection Manchester Council component from yaml configuration."""

    hass.async_create_task(
      discovery.async_load_platform(
        hass,
        Platform.SENSOR,
        DOMAIN,
        {
          CONF_POSTCODE: config[DOMAIN][CONF_POSTCODE],
          CONF_ADDRESS: config[DOMAIN][CONF_ADDRESS]
        },
        config
    ))
    return True
