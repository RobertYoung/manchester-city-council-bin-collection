import datetime
import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

COUNCIL_URL = "https://www.manchester.gov.uk/bincollections"

class ManchesterCouncilApi():
  def __init__(self, postcode, address) -> None:
    self._postcode = postcode
    self._address = address

  def fetch_data(self):
    req = Request(COUNCIL_URL)
    req.method = "POST"
    req.data = str.encode(f"mcc_bin_dates_search_term={self._postcode}&mcc_bin_dates_submit=Go")
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64)')

    fp = urlopen(req).read()
    page = fp.decode("utf8")
    soup = BeautifulSoup(page, features="html.parser")
    soup.prettify()

    address_id = None

    for address in soup.find("select").find_all('option'):
      if (address.text.startswith(self._address)):
        address_id = address.attrs['value']
        break

    if address_id is None:
      # _LOGGER.error(
      #   "Could not find address %s, %s", self._address, self._postcode
      # )
      return

    req_collection = Request(COUNCIL_URL)
    req_collection.method = "POST"
    req_collection.data = str.encode(f"mcc_bin_dates_uprn={address_id}&mcc_bin_dates_submit=Go")
    req_collection.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64)')

    fp = urlopen(req_collection).read()
    page = fp.decode("utf8")
    soup = BeautifulSoup(page, features="html.parser")
    soup.prettify()

    bins = []

    for bin_collection in soup.find_all("div", "collection"):
      colour_text: str = bin_collection.find("h3").text
      colour = re.findall(" (.*) Bin", colour_text)[0]
      bin_id = f'bin_{colour.replace("/", "_").replace(" ", "").lower()}'
      date_split = bin_collection.find("p", "caption").text.split()
      day = int(date_split[3])
      month = int(datetime.datetime.strptime(date_split[4], "%b").month)
      year = int(date_split[5])

      bins.append({
        "id": bin_id,
        "colour": colour,
        "next_collection": datetime.date(year, month, day),
        # "next_collection": f"{day}/{month}/{year}",
      })

    print(bins)
    return bins


