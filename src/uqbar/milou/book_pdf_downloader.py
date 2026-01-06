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

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from uqbar.utils.stats import get_random
from uqbar.utils.web import download_url_to_path

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
WAITER_TOTAL_TIME_BASE: float = 1.0

SLEEP_BASE: float = 0.1

NAV_SIZE_WINDOW: tuple[int, int] = (1920, 1080)


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _resolve_iterable(obj: Any) -> tuple[bool | None, Any | None]:
    """Placeholder"""
    if not obj:
        return None, None
    if isinstance(obj, Iterable):
        return True, obj
    else:
        return False, obj

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

    # Driver Main
    driver: webdriver = webdriver.Chrome(service=service, options=options)

    # Create window to maximize chance
    driver.maximize_window()
    driver.set_window_size(*nav_window_size)

    # Create ebook link list
    ebook_link_list: list[str] = []

    # Loop on each link
    for search_url in link_list:

        # Navigate to the URL
        driver.get(search_url)
        sleep(waiter_total_time_base + get_random())
        driver.refresh()
        sleep(waiter_total_time_base + get_random())

        # Find all <html> elements
        web_element_list = driver.find_element(By.XPATH, "/html")

        # Find all /html/body/div[2] elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []

        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=waiter_total_time_base)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/body/div[2]"
                    )
                )
                sleep(sleep_base + get_random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except Exception:
                pass
            finally:
                max_tries += 1

        # Find all /html/body/div[2]/div[6]/div[4] elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=waiter_total_time_base)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/div[6]/div[4]"
                    )
                )
                sleep(sleep_base + get_random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except Exception:
                pass
            finally:
                max_tries += 1

        # Find all /html/body/div[2]/div[6]/div[4]/div/div/div elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=waiter_total_time_base)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/div/div/div"
                    )
                )
                sleep(sleep_base + get_random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except Exception:
                pass
            finally:
                max_tries += 1

        # Find all /html/body/div[2]/div[6]/div[4]/div/div/div/div[2]/section[1]/ol
        # elements
        max_tries: int = 0
        curr_element_list: list[WebElement] | WebElement = []
        while not curr_element_list or max_tries < 3:
            try:
                wait = WebDriverWait(web_element_list, timeout=waiter_total_time_base)
                web_element_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        "//*/div[2]/section[1]/ol"
                    )
                )
                sleep(sleep_base + get_random())
                is_it, curr_element_list = _resolve_iterable(web_element_list)
            except Exception:
                pass
            finally:
                max_tries += 1

        # Iterate on 10 (first page) li items
        for idx in range(10):

            max_tries: int = 0
            wel_list: list[WebElement] | WebElement = []
            while not wel_list or max_tries < 3:
                try:

                    wait = WebDriverWait(web_element_list, timeout=waiter_total_time_base)

                    wel_list = wait.until(
                    lambda p: p.find_element(
                        By.XPATH,
                        f"//*/li[{idx}]/article/div[3]/h2/a"
                        )
                    )
                    sleep(sleep_base + get_random())
                    is_it, curr_element_list = _resolve_iterable(wel_list)

                except Exception:
                    pass
                finally:
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
                        except Exception:
                            continue
                    max_tries += 1
                    continue

                try:
                    web_link = wel_list.get_property("href")
                    web_ext = web_link.split(".")[-1]
                    if web_ext in query_format_list:
                        ebook_link_list.append(web_link)
                    sleep(sleep_base + get_random())
                except Exception:
                    continue
                finally:
                    max_tries += 1

    # Quit driver
    driver.quit()

    return ebook_link_list


def download_write(
    query_link_list: list[str],
    output_path: Path,
    *,
    write_dictionary: bool = True,
) -> None:

    if not output_path.is_dir():
        raise ValueError(f"output_path is not a directory: {output_path}")
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise e

    query_link_list = list(set(query_link_list))
    donwloaded_files: dict[str, list[str]] = dict()

    for query_link in query_link_list:

        try:
            strout, stderr = download_url_to_path(
                download_url=query_link,
                output_path=output_path,
            )
        except Exception:
            continue

        if write_dictionary:
            this_query: str = Path(query_link).name
            this_folder: str = output_path.name
            try:
                donwloaded_files[this_folder].append(this_query)
            except Exception:
                donwloaded_files[this_folder] = [this_query]

    if write_dictionary:
        output_file_path = output_path / "index.txt"
        with open(output_file_path, "a", encoding="utf-8") as file:
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
