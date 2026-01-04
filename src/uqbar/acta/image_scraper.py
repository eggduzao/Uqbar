# SPDX-License-Identifier: MIT
# uqbar/acta/image_scraper.py
"""
Acta Diurna | Image Scraper
===========================


micromamba install -c conda-forge spacy
micromamba install -c conda-forge sklearn

python -m spacy download en_core_web_sm

Overview
--------
Placeholder.

Metadata
--------
- Project: Acta diurna
- License: MIT
"""


# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import Generator, Iterator
from datetime import datetime as dt
import difflib
from io import BytesIO
from math import ceil
import numpy as np
from pathlib import Path
from PIL import Image
import requests
from time import sleep, time
from urllib.parse import urlparse, parse_qs, unquote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)

from uqbar.acta.utils import get_random


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
SEARCH_URL: str = f"https://duckduckgo.com/?q="


WAITER_TOTAL_TIME_BASE: float = 20.0
SLEEP_MIN_BASE: float = 0.1
SLEEP_MAX_BASE: float = 2.0
MAX_GLOBAL_TRIES: int = 2
MAX_LOCAL_TRIES: int = 5

NAV_SIZE_WINDOW: tuple[int, int] = (1920, 1080)


SCROLL_ACTION_DURATION: int = 150
SCROLL_TIMES: int = 1000
SCROLL_AMOUNG_BASIS: float = 1.0


# WebElement search dictionary where key is a title pointing to a vector with:
# [By name, By value, #empirical possible, #actual possible]
# ELEMENT_DICT: dict[str, list[str]] = {
#     "html": [By.TAG_NAME, "html", 1, 1],
#     "body": [By.TAG_NAME, "body", 1, 1],
#     "web": [By.ID, "web_content_wrapper", 1, 1],
#     "xpath_1": [By.XPATH, "//*[@id=\"react-layout\"]", 1, 1],
#     "xpath": [By.XPATH, "//*", 5188, 5188],
#     "section": [By.TAG_NAME, "section", 21, 6],
#     "ol_1": [By.TAG_NAME, "ol", 47, 9],
#     "ol_2": [By.TAG_NAME, "ol", 126, 9],
#     "figure": [By.TAG_NAME, "figure", 117, 100],
#     "xpath_2": [By.XPATH, "/html/body/*", 900, 0],
#     "img": [By.TAG_NAME, "img", 28800, 900],
# }
NAVBAR_DICT: dict[str, list[str]] = {
    "body": [By.TAG_NAME, "body", 1, 1],
    "web": [By.ID, "web_content_wrapper", 1, 1],
    "xpath": [By.XPATH, "//*", 5188, 5188],
    "section": [By.TAG_NAME, "section", 6, 6],
    "ol_1": [By.TAG_NAME, "ol", 47, 9],
    "ol_2": [By.TAG_NAME, "ol", 126, 9],
    "figure": [By.TAG_NAME, "figure", 117, 100],
}


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _get_search_url(query: str) -> str:
    return f"{SEARCH_URL}{query}&iar=images"


def _safeproof_click(
    driver: webdriver,
    element_or_list: WebElement | list[WebElement],
    *,
    wait_for_action: bool = False,
    timeout: int = 10,
) -> None:
    """
    Placeholder
    """

    _safe_click(
        driver: webdriver,
        web_element: WebElement,
        *,
        wait_for_action: bool = False,
        timeout: int = 10,
    ) -> None:

        try:

            # Wait until the element is actually clickable
            if wait_for_action:
                wait: WebDriverWait = WebDriverWait(driver, timeout)
                wait.until(EC.element_to_be_clickable(web_element))
            
            # Try standard Selenium click (mimics real user)
            web_element.click()
        except Exception:

            # Fallback: JavaScript click (bypasses overlays/visibility issues)
            driver.execute_script("arguments[0].click();", web_element)

    # 1. Determine if it's a list or single element
    if not isinstance(element_or_list, WebElement):

        for element in element_or_list:
            _safeproof_click(
                driver=driver,
                element_or_list=element_or_list,
                wait_for_action=wait_for_action,
                timeout=timeout,
            )
        return

    _safe_click(
        driver=driver,
        element_or_list=element_or_list,
        wait_for_action=wait_for_action,
        timeout=timeout,
    )
    return


def _click_on_xpath(driver: webdriver, xpath: str) -> None:
    """
    Placeholder
    """

    element_list: list[WebElement] = driver.find_elements(By.XPATH, xpath)

    for element in element_list:
        _safeproof_click(
            driver=driver,
            element_or_list=element,
        )


def _click_location_button(
    driver: webdriver,
    sleep_min_base: float,
) -> None:
    """
    Placeholder
    """

    element_list: list[WebElement] = driver.find_elements(
        By.CSS_SELECTOR,
        "[role='switch']",
    )

    for element in element_list:

        aria_checked: str = element.get_property("ariaChecked")

        if aria_checked is not None and aria_checked == "false":
            _safeproof_click(
                driver=driver,
                element_or_list=element,
            )
            break

        sleep(sleep_min_base + get_random())
    return


def _select_location_dropdown(
    sleep_min_base: float,
    sleep_max_base: float,
    *,
    target_text_list: list[str] = [
        "US (English)",
        "US",
        "USA",
        "Estados Unidos (inglês)",
        "Estados Unidos",
        "United States (english)",
        "United States"
    ]
) -> None:
    """
    Placeholder
    """

    # Change locale to US (English)
    _click_on_xpath('//*[@id="react-layout"]/div/div[2]/div/nav/div/ul/li[1]/div/div[1]')
    sleep(sleep_min_base + get_random())
    _click_on_xpath('//*[@id="react-layout"]/div/div[2]/div/nav/div/ul/li[1]/div/div[2]/div[2]/div[63]/div/div/div/span[2]')
    sleep(sleep_max_base + get_random())

    # Changing Image Sizes to Large
    _click_on_xpath('//*[@id="react-layout"]/div/div[2]/div/nav/div/ul/li[5]/div/div[1]')
    sleep(sleep_min_base + get_random())
    _click_on_xpath('//*[@id="react-layout"]/div/div[2]/div/nav/div/ul/li[5]/div/div[2]/div/div[4]/div')
    sleep(sleep_max_base + get_random())

    return


def _hyper_loop(
    waiter: WebDriverWait,
    curr_element_list: list[WebElement],
    max_global_tries: int,
    max_local_tries: int,
    sleep_min_base: float,
    sleep_max_base: float,
    *,
    reverse_search: float = False,
) -> list[WebElement]:

    for element_key, element_value in ELEMENT_DICT.items():

        by_tag = element_value[0]
        by_val = element_value[1]
        max_val = element_value[3] 
        if max_val == 0:
            max_val = element_value[2]

        flag_condition_met: bool = False
        if curr_element_list:
            prev_element_list: list[WebElement] = curr_element_list.copy()
            curr_element_list: list[WebElement] = []
            minimum_unique_elements: int = max_val if max_val > 10 else 1

        for _ in range(max_global_tries):

            if flag_condition_met:
                break

            for web_element in (reversed(prev_element_list) if reverse_search else prev_element_list):

                web_element_list: list[WebElement] = []
                for _ in range(max_local_tries):

                    # Find web elements
                    try:
                        web_element_list = waiter.until(EC.presence_of_all_elements_located((by_tag, by_val)))
                    except StaleElementReferenceException as sere:
                        pass
                    except TimeoutException as toe:
                        pass
                    except Exception as finale:
                        print(finale)
                        pass

                    if not web_element_list:
                        continue

                    curr_element_list.extend(web_element_list)
                    curr_element_list: list[WebElement] = _unique_remove_empty(curr_element_list)

                    if web_element_list:
                        web_element_list: list[WebElement] = []


                    sleep(sleep_min_base + get_random())

                    if len(curr_element_list) >= minimum_unique_elements:
                        flag_condition_met = True
                        break

                if flag_condition_met:
                    flag_condition_met = True
                    break

            if flag_condition_met:
                flag_condition_met = True
                break

        if flag_condition_met:
            flag_condition_met = True
            break

    return list(reversed(curr_element_list)) if reverse_search else curr_element_list


def _unique_remove_empty(
    element_list: list[WebElement],
) -> list[WebElement]:
    """
    - Removes empty inner lists
    - Removes stale/broken WebElements
    - Deduplicates WebElements globally (by element.id)
    - Preserves order and grouping
    """

    seen_ids: set[str] = set()
    cleaned: list[WebElement] = []

    try:
        for el in element_list:
            if el is None:
                continue

            try:
                el_id = el.id  # touching .id validates the element
            except StaleElementReferenceException as ein:
                continue

            if el_id in seen_ids:
                continue

            seen_ids.add(el_id)
            cleaned.append(el)

    except Exception as eout:
        cleaned = {x for x in element_list if x}
        cleaned = list(cleaned)

    return cleaned


def _get_uri_list(
    driver: webdriver,
    element_list: list[WebElement],
    *,
    sleep_min_base: int = SLEEP_MIN_BASE,
) -> list[str]:

    # Getting baseURI property
    uri_list: list[str] = []
    for element in element_list:

        try:
            _safeproof_click(
                driver=driver,
                element_or_list=element,
            )

            uri = element.get_property("baseURI")

        except Exception as e:
            pass

        uri_list.append(uri)
        sleep(sleep_min_base + get_random())


    return uri_list


def _remove_translate(web_element: str, base_url: str) -> str:
    """
    Extracts and decodes the real image URL from a DuckDuckGo image wrapper URL.
    - Ignores exact base_url matching (robust to variations)
    - Decodes percent-encoded URLs
    """

    # 1. Parse and query
    parsed = urlparse(web_element)
    query = parse_qs(parsed.query)

    # 2. DuckDuckGo image links usually store the real URL in `iai`
    if "iai" not in query:

        # 2.1.1. Normalize spaces encoded as '+'
        normalized = web_element.replace("+", " ")

        # 2.1.2. Attempt direct removal if web_element starts with base_url
        if normalized.startswith(base_url):
            remainder = normalized[len(base_url):]
        else:
            # 2.1.3. Fuzzy match (threshold ≈ 90%)
            ratio = difflib.SequenceMatcher(None, normalized[:len(base_url)], base_url).ratio()
            if ratio >= 0.90:
                remainder = normalized[len(base_url):]
            else:
                # 2.1.4. If no good match, fall back:
                #    Find the first encoded "http" that is not the main one.
                idx = normalized.find("http", 5)  # skip the initial "http"
                if idx == -1:
                    return ""  # nothing usable found
                remainder = normalized[idx:]

        # 2.1.5. Strip leading junk (&, ?, etc.)
        while remainder.startswith(("&", "?", "=")):
            remainder = remainder[1:]

        # 2.1.6. Decode URL-encoded parts
        decoded_url = unquote(remainder)

    else:

        # 2.2.1. Parse_qs returns lists
        encoded_url = query["iai"][0]

        # 2.2.2. Decode percent-encoding
        decoded_url = unquote(encoded_url)

    # 3. Remove trailing ?
    if "?" in decoded_url[-20:]:
        decoded_url = "?".join(decoded_url.split("?")[:-1])

    return decoded_url


def _scroll_down_refresh(
    driver: webdriver,
    *,
    action_duration: int = SCROLL_ACTION_DURATION,
    scroll_times: int = SCROLL_TIMES,
    scroll_amoung_basis: float = SCROLL_AMOUNG_BASIS,
) -> None:

    # Create Actions
    actions: ActionChains = ActionChains(driver, duration=action_duration)

    # Iterative scroll to mimic human-like behavior
    for i in range(0, 1000):
        actions.scroll_by_amount(
            delta_x=0,
            delta_y = ceil(scroll_amoung_basis + get_random())
        )

    # Perform sequential chain of actions
    actions.perform()

    return

# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def get_image_links(
    image_query: str,
    *,
    options: Options = Options(),
    service: Service = Service(ChromeDriverManager().install()),
    nav_window_size: tuple[int, int] = NAV_SIZE_WINDOW,
    waiter_total_time_base: int = WAITER_TOTAL_TIME_BASE,
    sleep_min_base: int = SLEEP_MIN_BASE,
    sleep_max_base: int = SLEEP_MAX_BASE,
    max_global_tries: int = MAX_GLOBAL_TRIES,
    max_local_tries: int = MAX_LOCAL_TRIES,
) -> list[str]:
    """
    Placeholder

    Going to make a whole Path walk:

    # WebElement search dictionary where key is a title pointing to a vector with:
    # [By name, By value, #empirical possible, #actual possible]
    ELEMENT_DICT: dict[str, list[str]] = {
        "html": [By.TAG_NAME, "html", 1, 1],
        "body": [By.TAG_NAME, "body", 1, 1],
        "web": [By.ID, "web_content_wrapper", 1, 1],
        "xpath_1": [By.XPATH, "//*[@id=\"react-layout\"]", 1, 1],
        "xpath_2": [By.XPATH, "//*", 5188, 5188],
        "section": [By.TAG_NAME, "section", 21, 6], # 6
        "ol_1": [By.TAG_NAME, "ol", 47, 9],
        "ol_2": [By.TAG_NAME, "ol", 126, 9],
        "figure": [By.TAG_NAME, "figure", 117, 117],
        # "xpath_3": [By.XPATH, "/html/body/*", 900, 0],
        # "img": [By.TAG_NAME, "img", 28800, 900],
    }

    """
    # options.add_argument("--headless=new")

    # --------- Initial Elements ---------

    # Input
    search_url: str = _get_search_url(image_query)

    # Driver Main
    driver: webdriver = webdriver.Chrome(service=service, options=options)

    # Create window to maximize chance
    driver.maximize_window()
    driver.set_window_size(*nav_window_size)

    # Navigate to the URL
    driver.get(search_url)
    sleep(5)
    driver.refresh()
    sleep(5)

    # Change location to 'on'
    _click_location_button(driver, sleep_min_base)

    # Switch location to USA and image to 'large'
    _select_location_dropdown(sleep_min_base, sleep_max_base)

    # --------- Main Loop ---------

    # Find all <html> elements
    waiter = WebDriverWait(driver, sleep_max_base + waiter_total_time + get_random())
    curr_element_list: list[WebElement] = waiter.until(EC.presence_of_all_elements_located((By.TAG_NAME, "html")))

    # Main Loop - Regular order
    web_element_list: list[WebElement] = _hyper_loop(
        waiter=waiter,
        curr_element_list=curr_element_list,
        max_global_tries=max_global_tries,
        max_local_tries=max_local_tries,
        sleep_min_base=sleep_min_base,
        sleep_max_base=sleep_max_base,
        reverse_search=False,
    )

    # Get baseURI property
    uri_list: list[str] = _get_uri_list(
        driver=driver,
        element_list=web_element_list,
    )

    # Create image links
    image_link_list: list[str] = []
    for uri in uri_list:
        image_link = _remove_translate(uri, search_url)
        image_link_list.append(image_link)

    # --------- Scroll Down ---------

    _scroll_down_refresh(driver)

    # --------- Main Loop ---------

    # Find all <html> elements
    waiter = WebDriverWait(driver, sleep_max_base+waiter_total_time_base+get_random())
    curr_element_list: list[WebElement] = waiter.until(EC.presence_of_all_elements_located((By.TAG_NAME, "html")))

    # Main Loop - Reversed
    web_element_list: list[WebElement] = _hyper_loop(
        waiter=waiter,
        curr_element_list=curr_element_list,
        max_global_tries=max_global_tries,
        max_local_tries=max_local_tries,
        sleep_min_base=sleep_min_base,
        sleep_max_base=sleep_max_base,
        reverse_search=True,
    )

    # Get baseURI property
    uri_list: list[str] = _get_uri_list(
        driver=driver,
        element_list=web_element_list,
    )

    # Create image links
    for uri in uri_list:
        image_link = _remove_translate(uri, search_url)
        image_link_list.append(image_link)

    # Quit driver
    driver.quit()

    # Post-process final image link list - remove duplicates
    image_link_list = list(set(image_link_list))

    return image_link_list

# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "get_image_links",
]


# -------------------------------------------------------------------------------------
# Test | python -m uqbar.acta.image_scraper > out.txt 2>&1
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":

