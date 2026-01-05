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

from collections.abc import Iterable
from pathlib import Path
from time import sleep
from typing import Any


import requests
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


from uqbar.utils.web import download_path_wget
from uqbar.utils.stats import get_random

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
WAITER_TOTAL_TIME_BASE: float = 2.0

SLEEP_BASE: float = 1.0

NAV_SIZE_WINDOW: tuple[int, int] = (1920, 1080)


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _resolve_iterable(obj: Any) -> tuple[bool, Any] | None:
    """Placeholder"""
    if not obj:
        return None
    if isinstance(obj, Iterable):
        return True, obj.copy()
    else:
        return False, obj.copy()

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
    waiter_total_time_base: float = WAITER_TOTAL_TIME_BASE,
    sleep_base: float = SLEEP_BASE,
) -> list[str] | None:
    """
    Placeholder
    """

    # Create ebook link list
    ebook_link_list: list[str] = []

    # Loop on each link
    for search_url in link_list:

        # Driver Main
        driver: webdriver = webdriver.Chrome(service=service, options=options)

        # Create window to maximize chance
        driver.maximize_window()
        driver.set_window_size(*nav_window_size)

        # Navigate to the URL
        driver.get(search_url)
        sleep(3.0)
        driver.refresh()
        sleep(3.0)

        # Find all <html> elements
        web_element_list = driver.find_element(By.XPATH, "/html")

        # Find all /html/body/div[2] elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=10)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/body/div[2]"
                    )
                )
                sleep(waiter_total_time_base + random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except (StaleElementReferenceException, TimeoutException) as es:
                pass
            except Exception as ex:
                pass
            max_tries += 1


        # Find all /html/body/div[2]/div[6]/div[4] elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=10)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/div[6]/div[4]"
                    )
                )
                sleep(waiter_total_time_base + random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except (StaleElementReferenceException, TimeoutException) as es:
                pass
            except Exception as ex:
                pass
            max_tries += 1

        # Find all /html/body/div[2]/div[6]/div[4]/div/div/div elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=10)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/div/div/div"
                    )
                )
                sleep(waiter_total_time_base + random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except (StaleElementReferenceException, TimeoutException) as es:
                pass
            except Exception as ex:
                pass
            max_tries += 1

        # Find all /html/body/div[2]/div[6]/div[4]/div/div/div/div[2]/section[1]/ol
        # elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=10)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/div[2]/section[1]/ol"
                    )
                )
                sleep(waiter_total_time_base + random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except (StaleElementReferenceException, TimeoutException) as es:
                pass
            except Exception as ex:
                pass
            max_tries += 1

        # Iterate on 10 (first page) li items
        for idx in range(10):

            max_tries: int = 0
            wel_list: list[WebElement] | WebElement = []
            while not wel_list or max_tries < 3:
                try: 

                    wait = WebDriverWait(web_element_list, timeout=10)

                    wel_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        f"//*/li[{idx}]/article/div[3]/h2/a"
                        )
                    )
                    sleep(sleep_base + get_random())
                    is_it, curr_element_list = _resolve_iterable(wel_list)

                except (StaleElementReferenceException, TimeoutException) as es:
                    pass
                except Exception as ex:
                    pass
                max_tries += 1

                if not wel_list:
                    break

                if is_it:
                    for wel in wel_list:
                        if not wel:
                            continue
                        try:
                            web_link = wel.get_property("href")
                            web_ext = web_link.split(".")[-1]
                            if web_ext in query_format_list:
                                ebook_link_list.append(web_link)
                            sleep(sleep_base + get_random())
                        except Exception as exx:
                            continue

                        if not wel:
                            continue
                    continue

                try:
                    web_link = wel_list.get_property("href")
                    web_ext = web_link.split(".")[-1]
                    if web_ext in query_format_list:
                        ebook_link_list.append(web_link)
                    sleep(sleep_base + get_random())

        # Quit driver
        driver.quit()

    return ebook_link_list


def download_write(
    query_link_list: list[str],
    output_path: Path,
    *,
    write_dictionary=True,
) -> None:

    if not output_path.exists():
        raise FileNotFoundError(f"output_path does not exist: {output_path}")
    if not output_path.is_file():
        raise ValueError(f"output_path is not a file: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    donwloaded_files: dict[str, list[str]] = dict()

    for query_link in query_link_list:
        strout, stderr = download_path_wget(
            download_url=query_link,
            output_path=output_path,
        )
        if write_dictionary:
            this_query: str = Path(query_link).name
            this_folder: str = output_path.name
            try:
                donwloaded_files[this_folder].append(this_query)
            except Exception as e:
                donwloaded_files[this_folder] = [this_query]

    if write_dictionary:
        output_file_path = output_path / "index.txt"
        with open(output_file_path, "w", encoding="utf-8") as file:
            for key, val in donwloaded_files.items():
                file.write(f"### {key}:\n")
                for el in val:
                    file.write(f"{el}\n")
                file.write(f"{"-"*100}\n\n")


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "search_for_links",
    "download_write",
]
