# Manchester City Council Bin Collection Home Assistant Component

This [Home Assistant](https://www.home-assistant.io/) component will scrape the [Manchester City Council](https://www.manchester.gov.uk/bincollections) webpage to find out a households bin collection and create a sensor for each type of bin.

For example:

| Entity                  | State       | Attributes                                                                                                                                                                |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sensor.black_grey_bin` | `today`     | **colour:** black / grey</br>**next_collection:** 2022-06-09</br>**days:** 0</br>**icon:** mdi:delete</br>**friendly_name:** Black / Grey bin</br>**icon_color:** #5a5858 |
| `sensor.blue_bin`       | `tomorrow`  | **colour:** blue</br>**next_collection:** 2022-06-10</br>**days:** 1</br>**icon:** mdi:delete</br>**friendly_name:** Blue bin</br>**icon_color:** #3880de                 |
| `sensor.brown_bin`      | `this_week` | **colour:** brown</br>**next_collection:** 2022-06-11</br>**days:** 8</br>**icon:** mdi:delete</br>**friendly_name:** Brown bin</br>**icon_color:** #5e3838               |
| `sensor.green_bin`      | `next_week` | **colour:** green</br>**next_collection:** 2022-06-17</br>**days:** 15</br>**icon:** mdi:delete</br>**friendly_name:** Green bin</br>**icon_color:** #158f15              |

![Example Home Assistant dashboard](/assets/images/dashboard_example.png "Example Home Assistant dashboard")

# Installation

The recommended way to install this component is using [HACS](https://hacs.xyz/).

## Configuration

Add the following to your `configuration.yaml`

```
bin_collection_manchester_council:
  postcode: m201aa
  address: 43 Mauldeth Road West
```

If you want to change the icon colours of the bins, you will need the [custom-ui](https://github.com/Mariusthvdb/custom-ui) plugin.

An example `customize.yaml` to update the colours:

```
sensor.blue_bin:
  icon_color: "#3880de"
sensor.green_bin:
  icon_color: "#158f15"
sensor.brown_bin:
  icon_color: "#5e3838"
sensor.black_grey_bin:
  icon_color: "#5a5858"
```

# Automations

Now that you have the bin sensors added to your Home Assistant you can start doing some cool automations.

For this example automation, you will need to create an `input_boolean` to track when the bins have been completed:

```yaml
bins_completed:
    name: Bins Completed
    icon: mdi:check-circle
    initial: on
```

Add your bin sensors to a group:

```yaml
bins:
  name: Bins
  entities:
    - sensor.black_grey_bin
    - sensor.blue_bin
    - sensor.brown_bin
    - sensor.green_bin
```

![Node Red Example](/assets/images/nodered_example.png "Node Red Example")

- Check if bins are being collected tomorrow and set `input_boolean.bins_completed` to `off` if there are
- From 17:00 to 00:00 every 30 mins, send a notification to a mobile device as a reminder
- Mark the bins collected either via the mobile notification action or in Home Assistant

![Bin Notification Example](/assets/images/mobile_notification.png "Bin Notification Example")
![Bin Notification Action Complete Example](/assets/images/mobile_notification_complete_action.png "Bin Notification Action Complete Example")

# Development

Either, copy the `custom_components` to your Home Assistant config directory, or spin up a local instance using [Home Assistant Core](https://github.com/home-assistant/core). Using `.devcontainer` within the core repository will enable debugging as it will attach to the process.

```sh
cp -R ~/git/home-assistant-core/config/custom_components/bin_collection_manchester_council ./custom_components
```
