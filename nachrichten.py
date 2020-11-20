#!/usr/bin/env python3

from __future__ import annotations

import datetime
import json
import re
import sys
from typing import Optional

import requests
from bs4 import BeautifulSoup

TAGESSCHAU_URL_TEMPLATE = "https://www.tagesschau.de{}"
TAGESSCHAU_ARCHIVE_URL_TEMPLATE = TAGESSCHAU_URL_TEMPLATE.format(
    "/multimedia/video/videoarchiv2~_date-{:%Y%m%d}.html"
)

ZDF_URL_TEMPLATE = "https://www.zdf.de{}"
ZDF_SENDUNG_VERPASST_URL_TEMPLATE = ZDF_URL_TEMPLATE.format(
    "/sendung-verpasst?airtimeDate={:%Y-%m-%d}"
)


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    return BeautifulSoup(html, features="lxml")


def get_latest_tagesschau_page_url_for_date(date: datetime.date) -> Optional[str]:
    tagesschau_archive_url = TAGESSCHAU_ARCHIVE_URL_TEMPLATE.format(date)
    soup = get_soup(tagesschau_archive_url)

    tagesschau_entries = []
    for div in soup.find_all("div", {"class": "mod modA modThumbnail"}):
        h4 = div.find("h4")
        if not h4 or h4.text != "tagesschau":
            continue
        a = h4.find("a")
        p = div.find("p", {"class": "dachzeile"})
        if not a or not p:
            continue
        tagesschau_url = TAGESSCHAU_URL_TEMPLATE.format(a["href"])
        dt = datetime.datetime.strptime(p.text, "%d.%m.%Y %H:%M Uhr")
        tagesschau_entries.append((dt, tagesschau_url))

    if not tagesschau_entries:
        return None
    # Sort by date, oldest first
    tagesschau_entries.sort(key=lambda entry: entry[0])
    return tagesschau_entries[-1][1]


def get_tagesschau_video_url_from_page(url: str) -> Optional[str]:
    soup = get_soup(url)
    download_links = soup.find_all(
        "a", {"href": re.compile("//download\.media\.tagesschau\.de/.*")}
    )
    if not download_links:
        return None
    highest_quality = download_links[-1]
    return f"https:{highest_quality['href']}"


def get_latest_heute_page_url_for_date(date: datetime.date) -> Optional[str]:
    zdf_sendung_verpasst_url = ZDF_SENDUNG_VERPASST_URL_TEMPLATE.format(date)
    soup = get_soup(zdf_sendung_verpasst_url)

    heute_entries = []
    for article in soup.find_all("article", {"class": "b-content-teaser-item"}):
        a = article.find("a", {"class": "teaser-title-link"})
        if "ZDF heute Sendung" not in a["title"]:
            continue
        heute_url = ZDF_URL_TEMPLATE.format(a["href"])
        # "Sendung verpasst" page has entries sorted by time,
        # so we don't need to sort them ourselves :)
        heute_entries.append(heute_url)

    if not heute_entries:
        return None
    return heute_entries[-1]


def get_heute_video_url_from_page(url: str) -> Optional[str]:
    soup = get_soup(url)
    download_button = soup.find("button", {"class": "download-btn"})
    if not download_button:
        return None
    data_dialog = json.loads(download_button["data-dialog"])
    api_token = data_dialog["apiToken"]
    content_url = data_dialog["contentUrl"]
    # This is from https://www.zdf.de/ZDFplayer/configs/zdf/zdf2016/configuration.json
    # The value from the download button is "zdf_pd_download_1", but it
    # doesn't seem to work with every video ("heute 12 Uhr" was hiding
    # the download button, for example, and the API response didn't
    # have any download URLs)
    player_id = "ngplayer_2_4"
    content_url = content_url.format(playerId=player_id)
    response = requests.get(content_url, headers={"Api-Auth": f"Bearer {api_token}"})
    response.raise_for_status()
    data = response.json()
    # - "priorityList" can have multiple objects, each being in a
    #   different format
    # - "formitaeten" always seems to be a one-element array
    # - "qualities" should be obvious, see the "quality" and "hd" keys
    #   in each object
    qualities = data["priorityList"][0]["formitaeten"][0]["qualities"]
    qualities.sort(key=lambda entry: ["hd", "veryhigh", "high"].index(entry["quality"]))
    # YES, THIS IS A VIDEO!
    return qualities[0]["audio"]["tracks"][0]["uri"]


def main_tagesschau() -> None:
    today = datetime.date.today()
    if not (tagesschau_url := get_latest_tagesschau_page_url_for_date(today)):
        tagesschau_archive_url = TAGESSCHAU_ARCHIVE_URL_TEMPLATE.format(today)
        print(
            f"Could not find tagesschau page URL, please check {tagesschau_archive_url} manually"
        )
        sys.exit(1)
    if not (tagesschau_video_url := get_tagesschau_video_url_from_page(tagesschau_url)):
        print(
            f"Could not get tagesschau video URL from page, please check {tagesschau_url} manually"
        )
        sys.exit(1)
    print(tagesschau_video_url)


def main_heute() -> None:
    today = datetime.date.today()
    if not (heute_url := get_latest_heute_page_url_for_date(today)):
        zdf_sendung_verpasst_url = ZDF_SENDUNG_VERPASST_URL_TEMPLATE.format(today)
        print(
            f"Could not find ZDF heute page URL, please check {zdf_sendung_verpasst_url} manually"
        )
        sys.exit(1)
    if not (heute_video_url := get_heute_video_url_from_page(heute_url)):
        print(
            f"Could not get ZDF heute video URL from page, please check {heute_url} manually"
        )
        sys.exit(1)
    print(heute_video_url)


def main() -> None:
    try:
        name = sys.argv[1]
        if name != "tagesschau" and name != "heute":
            raise ValueError()
    except (IndexError, ValueError):
        print(f"usage: {sys.argv[0]} [tagesschau|heute]")
        sys.exit(1)
    if name == "tagesschau":
        main_tagesschau()
    if name == "heute":
        main_heute()


if __name__ == "__main__":
    main()
