import requests as rq
import re
from pathlib import Path
import json
import csv
import time
import gzip
import math
from pdfminer.high_level import extract_text
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Iterator
from fake_useragent import UserAgent

from data import DataHandler, Provider, Providers

base_dir = Path(__file__).resolve().parent.parent

data_dir = base_dir / "data"
etfs_pdf_file = data_dir / "etfs.pdf"
etfs_txt_file = data_dir / "etfs.txt"
isins_data_file = data_dir / "isins"
missing_isins_file = data_dir / "isins_missing"
frankfurt_data_file = data_dir / "frankfurt_data.csv"
frankfurt_info_file = data_dir / "frankfurt_info.json"
proxies_data_file = data_dir / "proxies.txt"
if not data_dir.is_dir():
    data_dir.mkdir()

provider: Provider = Providers.frankfurt


def fetchen_wir(isins, timeout=3, headless=False) -> Iterator[DataHandler]:
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    not_found_on_ex = []
    probably_not_found_on_ex = []
    todo = len(isins)
    print(f"todo: {todo}")
    max_req_time = 0
    req_times = 0
    req_times_n = 0
    avg_req_time = 0
    info_data = None

    # proxy_gen = rq.get("https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all").text.split("\n")
    while not (proxies := rq.get("http://localhost:8000/api/proxies").json()):
        time.sleep(1)

    proxy, reqtime = list(proxies.items())[0]
    print(proxy, reqtime)
    timeout += reqtime
    timeout *= 1.5
    timeout = math.ceil(timeout)
    print("timeout:", timeout)

    opts.add_argument(f"--proxy-server={proxy}")
    ua_gen = UserAgent(os="windows", min_percentage=10.0)
    useragent = ua_gen.random
    opts.add_argument(f"user-agent={useragent}")
    print("user-agent:", useragent)
    # opts.proxy = Proxy(
    #     {
    #         "proxyType": ProxyType.MANUAL,
    #         # 'httpProxy': "http://127.0.0.1:8888",
    #         "httpsProxy": f"https://{proxy}",
    #     }
    # )

    with webdriver.Chrome(options=opts) as driver:
        driver.execute_cdp_cmd("Performance.enable", {})
        driver.get(provider.url)
        try:
            inp = WebDriverWait(driver, timeout * 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, provider.css_input_selector)
                )
            )
        except (NoSuchElementException, TimeoutException) as e:
            driver.get_screenshot_as_file("screenshot.png")
            raise e
        for i in range(todo):
            isin = isins[i]
            data_not_available = False
            print(f"\r#{todo}", end=" ", flush=True)
            while True:
                inp.clear()
                inp.send_keys(isin)
                starttime = time.time()
                try:
                    # https://www.wallstreet-online.de/_rpc/json/search/auto/searchInst/IE00B27YCP72
                    info_request = driver.wait_for_request(
                        provider.search_param, timeout=timeout
                    )
                    # """https://api.boerse-frankfurt.de/v1/global_search/limitedsearch/de?searchTerms=IE00B1FZS798"""
                    reqtime = time.time() - starttime
                    req_times += reqtime
                    req_times_n += 1
                    decompressed = gzip.decompress(info_request.response.body)
                    info_data = json.loads(decompressed)
                    if not info_data:
                        data_not_available = True
                    else:
                        info_data = info_data[0][0]
                    break
                except TimeoutException:
                    req_times += timeout
                    req_times_n += 1
                    continue
            if data_not_available:
                probably_not_found_on_ex.append(isin)
                continue
            inp.send_keys(Keys.RETURN)
            starttime = time.time()
            try:
                performance_request = driver.wait_for_request(
                    provider.data_search_param, timeout=timeout
                )
                reqtime = round(time.time() - starttime, 3)
                req_times += reqtime
                req_times_n += 1
                todo -= 1
                if reqtime > max_req_time:
                    max_req_time = reqtime
                if max_req_time > avg_req_time:  # optimize the timeout
                    timeout = math.ceil(max_req_time)
                try:
                    decompressed = gzip.decompress(performance_request.response.body)
                except gzip.BadGzipFile:
                    probably_not_found_on_ex.append(isin)
                    continue

                performance_data = json.loads(decompressed)
                if "isin" in performance_data:
                    del performance_data["isin"]
                if "messages" in performance_data:
                    not_found_on_ex.append(isin)
                    continue
                for v in performance_data.values():
                    if not v:
                        break
                else:
                    yield provider.data_handler.from_data(
                        isin, info_data, performance_data
                    )
            except TimeoutException:
                todo -= 1
                probably_not_found_on_ex.append(isin)
                req_times += timeout
                req_times_n += 1
            avg_req_time = round(req_times / req_times_n, 3)
        driver.quit()

    print("max req time:", max_req_time)
    print("timeout:", timeout)
    print(len(not_found_on_ex), "isins are NOT available on boerse-frankfurt.de")
    print(
        len(probably_not_found_on_ex),
        "isins are PROBABLY NOT available on boerse-frankfurt.de",
    )
    info = {}
    if frankfurt_info_file.exists():
        info = json.loads(frankfurt_info_file.read_text())
    info["frankfurt"]["isins_not_available"] = not_found_on_ex
    info["frankfurt"]["isins_failed"] = probably_not_found_on_ex
    frankfurt_info_file.write_text(json.dumps(info, indent=4))


def get_this_shit():
    der_link = "https://assets.traderepublic.com/assets/files/Sparplan-Universum.pdf"
    print(f"getting {der_link}")
    etfs_pdf_file.write_bytes(rq.get(der_link).content)
    print("extracting text")
    etfs_txt_file.write_text(extract_text(etfs_pdf_file))


def da_parsen_wir_rein(keep: bool):
    isins = []
    pages = (
        etfs_txt_file.read_text().strip().split("SPARPLAN-UNIVERSUM DEUTSCHLAND")[:-1]
    )
    shitty_regex = re.compile(r"([A-Z]{2})([A-Z0-9]{9})([0-9]{1})", re.M)
    for page_number in range(len(pages)):
        page = pages[page_number]
        for match in shitty_regex.findall(page):
            isin = "".join(match)
            isins.append(isin)
    isins_data_file.write_text("\n".join(isins))
    print(f"{len(isins)} etf results")
    if not keep:
        etfs_pdf_file.unlink()
        etfs_txt_file.unlink()


def data_generator(headless=True) -> Iterator[DataHandler]:
    """Data generator. Uses data_dir and selenium to fetch ISINs from TradeRepublic PDF.

    Args:
        n (int, optional): Number of data objects ("FrankfurtData") to generate. Defaults to -1 which produces as many as possible.

    Yields:
        Iterator[FrankfurtData]
    """
    if not isins_data_file.exists():
        if not etfs_pdf_file.exists() or not etfs_txt_file.exists():
            get_this_shit()
        da_parsen_wir_rein(keep=True)

    isins_not_available = []
    if frankfurt_info_file.exists():
        info = json.loads(frankfurt_info_file.read_text())
        if "isins_not_available" in info["frankfurt"]:
            isins_not_available = info["frankfurt"]["isins_not_available"]

    isins_total = isins_data_file.read_text().split("\n")
    isins_not_stored = []
    print("Total ISINs:", len(isins_total))
    if frankfurt_data_file.exists():
        frankfurt_data_store = []
        isin_to_fdata_map = {}
        with frankfurt_data_file.open("r+") as f:
            reader = csv.reader(f)
            if not next(reader, None):  # Skip header if exists, write headers otherwise
                writer = csv.writer(f)
                writer.writerow(provider.data_handler.dict_elems.keys())
            for row in reader:
                fData = provider.data_handler.from_csv(row)
                isin_to_fdata_map[fData.isin] = fData
                frankfurt_data_store.append(fData)
        for isin in isins_total:
            if isin in isin_to_fdata_map:
                fData = isin_to_fdata_map[isin]
                for v in fData.performance.values():
                    if not v:
                        break
                else:
                    yield fData
            elif isin not in isins_not_available:
                isins_not_stored.append(isin)
    else:
        # Write headers
        with frankfurt_data_file.open("w") as f:
            writer = csv.writer(f)
            writer.writerow(provider.data_handler.dict_elems.keys())
        isins_not_stored = isins_total

    with frankfurt_data_file.open("a") as f:
        writer = csv.writer(f)
        for fData in fetchen_wir(isins_not_stored, headless=headless):
            writer.writerow(fData.to_csv())
            yield fData


def get_info():
    if frankfurt_info_file.exists():
        info = json.loads(frankfurt_info_file.read_text())
    else:
        info = {"frankfurt": {"timeframe": provider.data_handler.possible_timespans}}
        frankfurt_info_file.write_text(json.dumps(info, indent=4))
    return info


def analyze_data(time_span="years1"):
    sorted_data = []
    for fdata in data_generator():
        if time_span not in fdata.performance:
            continue
        if performance_in_time_span := fdata.performance[time_span]:
            if change_in_percent := performance_in_time_span["changeInPercent"]:
                index_of_insertion = 0
                for i in range(len(sorted_data)):
                    if change_in_percent > sorted_data[i][0]:
                        index_of_insertion = i
                    else:
                        break
                send_to_queue = (index_of_insertion, (change_in_percent, fdata))
                sorted_data.insert(*send_to_queue)
                yield send_to_queue


if __name__ == "__main__":
    list(analyze_data())
