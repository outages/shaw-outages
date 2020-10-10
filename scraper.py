#!/usr/bin/env python3

import logging
import requests
import json
from bs4 import BeautifulSoup

REGIONS = ['bc interior', 'lower mainland', 'vancouver island',
           'northern alberta', 'southern alberta', 'saskatchewan', 'manitoba', 'ontario']
BASE_URL = 'https://support.shaw.ca'
LIST_BASE_URL = f"{BASE_URL}/t5/service-updates-outages/tkb-p/service-updates/label-name/"


def extract_outage_card(outage_card):
    outage = {}

    title_el = outage_card.select("h3")
    if len(title_el) > 0:
        outage["title"] = title_el[0].text

    more_details_el = outage_card.select(".more-details a")
    if len(more_details_el) > 0:
        outage["url"] = more_details_el[0].attrs["href"]
        outage_id = outage["url"].split("/")[-1]
    else:
        outage_id = "MISSING"

    summary_el = outage_card.select(".body-summary-raw")
    if len(more_details_el) > 0:
        summary_texts = summary_el[0].findAll(text=True)
        outage["summary"] = "".join(summary_texts)

    return outage_id, outage


def parse_region(region):
    region_url = f"{LIST_BASE_URL}{region}"

    r = requests.get(region_url)
    if r.status_code != 200:
        logging.warning(
            f"Could not fetch {region_url}. Status code received: {r.status_code}. Full output: {r.text}")
        return {}, True

    soup = BeautifulSoup(r.text, 'html.parser')
    outages_el = soup.select(".service-outage-card-inner")

    outages = {extract_outage_card(outage_el)[0]: extract_outage_card(outage_el)[
        1] for outage_el in outages_el}

    return outages, False


def main():
    regions_results = {}
    for region in REGIONS:
        parsed_region, invalid = parse_region(region)

        if not invalid:
            regions_results[region] = parsed_region

    with open("shaw_outages.json", "w") as outfile:
        json.dump(regions_results, outfile, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
