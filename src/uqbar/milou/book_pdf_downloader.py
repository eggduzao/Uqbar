"""
pip install yt-dlp
pip install ffmpeg
---
brew install ffmpeg
micromamba install -c conda-forge yt-dlp
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
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


from uqbar.utils.download import download_path_wget ########### MAKE UTILS GLOBAL


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
WAITER_TOTAL_TIME_BASE: float = 20.0

SLEEP_MIN_BASE: float = 0.1

SLEEP_MAX_BASE: float = 2.0

MAX_GLOBAL_TRIES: int = 2

MAX_LOCAL_TRIES: int = 5

NAV_SIZE_WINDOW: tuple[int, int] = (1920, 1080)


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
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


def _get_uri_list(
    driver: webdriver,
    element_list: list[WebElement],
) -> list[str]:

    # Getting baseURI property
    uri_list: list[str] = []
    for element in element_list:

        try:
            _safeproof_click(
                driver=driver,
                element_or_list=element,
            )

            uri = element.get_property("baseURI") ############ CHECK

        except Exception as e:
            pass

        uri_list.append(uri)
        sleep(sleep_min_base + get_random())


    return uri_list


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def search_for_links(
    link_list: list[str],
    query_format_list: list[str],
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
    """

    # Loop on each link
    for search_url in link_list:

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

        # Find all <html> elements
        waiter = WebDriverWait(
            driver,
            sleep_max_base + waiter_total_time_base + get_random()
        )
        web_element_list: list[WebElement] = waiter.until(
            EC.presence_of_all_elements_located(
                (By.TAG_NAME, "html")
            )
        )

        # Find all <body> elements
        waiter = WebDriverWait(
            driver,
            sleep_max_base + waiter_total_time_base + get_random()
        )
        web_element_list: list[WebElement] = waiter.until(
            EC.presence_of_all_elements_located(
                (By.TAG_NAME, "body")
            )
        )

        # Find all <div> elements
        waiter = WebDriverWait(
            driver,
            sleep_max_base + waiter_total_time_base + get_random()
        )
        web_element_list: list[WebElement] = waiter.until(
            EC.presence_of_all_elements_located(
                (By.TAG_NAME, "div")
            )
        )

        # Get baseURI property
        uri_list: list[str] = _get_uri_list(
            driver=driver,
            element_list=web_element_list,
        )

        # Create image links
        ebook_link_list: list[str] = []
        for uri in uri_list:
            ebook_link = _clean_uri(uri) ############# IMPLEMENT
            ebook_link_list.append(ebook_link)

        # Quit driver
        driver.quit()

        return ebook_link_list


def download_write(
            query_link_list=query_link_list,
            output_path=output_path,
            write_dictionary=True,
) -> None:



# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "search_for_links",
    "download_write",
]
