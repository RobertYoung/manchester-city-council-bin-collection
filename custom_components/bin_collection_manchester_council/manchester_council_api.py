import datetime
from http import HTTPStatus
import json
import logging

from dateutil.relativedelta import relativedelta
import requests

from .const import REQUEST_USER_AGENT

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": REQUEST_USER_AGENT,
}
TIMEOUT = 5


class ManchesterCouncilApi:
    def __init__(self, postcode, address) -> None:
        self._postcode = postcode
        self._address = address
        self.authorization = None
        self.address_id = None
        self.uprn = None
        self.bin_info = None

    def fetch_data(self):
        self.authorization = self.fetch_authorisation()
        self.address_id = self.fetch_address_id()
        self.uprn = self.fetch_uprn()
        self.bin_info = self.fetch_bin_info()

        bins = []

        bins.append(self.calc_bin("ahtm_dates_black_bin", "black_grey"))
        bins.append(self.calc_bin("ahtm_dates_blue_pulpable_bin", "blue"))
        bins.append(self.calc_bin("ahtm_dates_green_organic_bin", "green"))
        bins.append(self.calc_bin("ahtm_dates_brown_commingled_bin", "brown"))

        return bins

    def fetch_authorisation(self):
        resp = requests.get(
            "https://manchester.form.uk.empro.verintcloudservices.com/api/citizen?archived=Y&preview=false&locale=en",
            headers=HEADERS,
            timeout=TIMEOUT,
        )

        authorization = resp.headers["authorization"]

        if resp.status_code != HTTPStatus.OK:
            _LOGGER.error(
                "Unable to fetch authorization key : %s",
                resp.status_code,
            )
            return

        return authorization

    def fetch_address_id(self):
        prop_search_resp = {
            "name": "sr_bin_coll_day_checker",
            "data": {"addressnumber": "", "streetname": "", "postcode": self._postcode},
            "email": "",
            "caseid": "",
            "xref": "",
            "xref1": "",
            "xref2": "",
        }

        prop_search_resp = requests.post(
            "https://manchester.form.uk.empro.verintcloudservices.com/api/custom?action=widget-property-search&actionedby=location_search_property&loadform=true&access=citizen&locale=en",
            json=prop_search_resp,
            headers={
                "User-Agent": REQUEST_USER_AGENT,
                "Authorization": self.authorization,
            },
            timeout=TIMEOUT,
        )

        if prop_search_resp.status_code != HTTPStatus.OK:
            _LOGGER.error(
                "Unable to fetch addresses from manchester council api : %s",
                prop_search_resp.status_code,
            )
            return

        prop_search_obj = json.loads(prop_search_resp.text)

        address_id = None

        for address in prop_search_obj["data"]["prop_search_results"]:
            if address["label"].startswith(self._address.upper()):
                address_id = address["value"]
                break

        if address_id is None:
            _LOGGER.error(
                "Could not find address %s, %s", self._address, self._postcode
            )
            return

        return address_id

    def fetch_uprn(self):
        retreive_property_data = {
            "name": "sr_bin_coll_day_checker",
            "data": {"object_id": self.address_id},
            "email": "",
            "caseid": "",
            "xref": "",
            "xref1": "",
            "xref2": "",
        }

        retreive_property_resp = requests.post(
            "https://manchester.form.uk.empro.verintcloudservices.com/api/custom?action=retrieve-property&actionedby=_KDF_optionSelected&loadform=true&access=citizen&locale=en",
            json=retreive_property_data,
            headers={
                "User-Agent": REQUEST_USER_AGENT,
                "Authorization": self.authorization,
            },
            timeout=TIMEOUT,
        )

        return json.loads(retreive_property_resp.text)["data"]["UPRN"]

    def fetch_bin_info(self):
        today = datetime.datetime.today()
        future = today + relativedelta(months=1)
        bin_info_data = {
            "name": "sr_bin_coll_day_checker",
            "data": {
                "uprn": self.uprn,
                "nextCollectionFromDate": today.strftime("%Y-%m-%d"),
                "nextCollectionToDate": future.strftime("%Y-%m-%d"),
            },
            "email": "",
            "caseid": "",
            "xref": "",
            "xref1": "",
            "xref2": "",
        }

        bin_info_resp = requests.post(
            "https://manchester.form.uk.empro.verintcloudservices.com/api/custom?action=bin_checker-get_bin_col_info&actionedby=_KDF_custom&loadform=true&access=citizen&locale=en",
            json=bin_info_data,
            headers={
                "User-Agent": REQUEST_USER_AGENT,
                "Authorization": self.authorization,
            },
            timeout=TIMEOUT,
        )

        bin_info_obj = json.loads(bin_info_resp.text)

        return bin_info_obj["data"]

    def calc_bin(self, ahtm_key, colour):
        bin_date = self.bin_info[ahtm_key].split(" ")[0]
        next_collection = datetime.datetime.strptime(bin_date, "%d/%m/%Y")

        return {
            "id": f"bin_{colour}",
            "colour": colour,
            "next_collection": next_collection.date(),
        }
