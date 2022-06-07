# Manchester City Council Bin Collection Home Assistant Component

This [Home Assistant](https://www.home-assistant.io/) component will scrape the [Manchester City Council](https://www.manchester.gov.uk/bincollections) webpage to find out a households collection and create a sensor for each type of bin.

For example:

| Entity                  | State            | Attributes                                                                                                                                                                |
| ----------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sensor.black_grey_bin` | `today`          | **colour:** black / grey</br>**next_collection:** 2022-06-09</br>**days:** 0</br>**icon:** mdi:delete</br>**friendly_name:** Black / Grey bin</br>**icon_color:** #5a5858 |
| `sensor.blue_bin`       | `tomorrow`       | **colour:** blue</br>**next_collection:** 2022-06-10</br>**days:** 1</br>**icon:** mdi:delete</br>**friendly_name:** Blue bin</br>**icon_color:** #3880de                 |
| `sensor.brown_bin`      | `next_week`      | **colour:** brown</br>**next_collection:** 2022-06-17</br>**days:** 8</br>**icon:** mdi:delete</br>**friendly_name:** Brown bin</br>**icon_color:** #5e3838               |
| `sensor.green_bin`      | `following_wwek` | **colour:** green</br>**next_collection:** 2022-06-24</br>**days:** 15</br>**icon:** mdi:delete</br>**friendly_name:** Green bin</br>**icon_color:** #158f15              |


# Installation

The recommended way to install this component is using [HACS](https://hacs.xyz/).

## Configuration

Add the following to your `configuration.yaml`

```
bin_collection_manchester_council:
  postcode: m14hj
  address: 2 New York Street
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

## Admin

```sh
cp -R ~/git/home-assistant-core/config/custom_components/bin_collection_manchester_council ./custom_components
```
