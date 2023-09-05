from collections.abc import Callable
import requests as rq
import re
from pathlib import Path
import json
import stat
import time
import datetime
import gzip
import math
from pdfminer.high_level import extract_text
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from typing import Any, Generator

base_dir = Path(__file__).resolve().parent.parent

data_dir = base_dir / "data"
etfs_pdf_file = data_dir / "etfs.pdf"
etfs_txt_file = data_dir / "etfs.txt"
isins_data_file = data_dir / "isins"
missing_isins_file = data_dir / "isins_missing"
frankfurt_data_file = data_dir / "franfurt_data.json"
if not data_dir.is_dir():
    data_dir.mkdir()

tmp_dir = base_dir / "tmp"
update_geckodriver_script_file = tmp_dir / "update_geckodriver.sh"


# if not tmp_dir.is_dir():
#     tmp_dir.mkdir()
def flatten(l):
    return [item for sublist in l for item in sublist]


def create_geckodriver_update_script():
    geckodriver_tar = tmp_dir / "geckodriver.tar.xz"
    script = f"""json=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest)
if [[ $(uname) == "Darwin" ]]; then
    url=$(echo "$json" | jq -r '.assets[].browser_download_url | select(contains("macos") and (contains(".asc") | not))')
elif [[ $(uname) == "Linux" ]]; then
    url=$(echo "$json" | jq -r '.assets[].browser_download_url | select(contains("linux64") and (contains(".asc") | not))')
else
    echo "can't determine OS"
    exit 1
fi
echo $url
curl -s -L "$url" | tar xzv -C {tmp_dir}
chmod +x {tmp_dir / 'geckodriver'}"""
    update_geckodriver_script_file.write_text(script)
    update_geckodriver_script_file.chmod(
        update_geckodriver_script_file.stat().st_mode | stat.S_IEXEC
    )


def update_geckodriver():
    if not update_geckodriver_script_file.exists():
        create_geckodriver_update_script()
    from subprocess import Popen, PIPE

    session = Popen(
        ["bash", update_geckodriver_script_file.as_posix()], stdout=PIPE, stderr=PIPE
    )
    stdout, stderr = session.communicate()

    if stderr:
        raise Exception("Error " + str(stderr))

    print(str(stdout))


class FrankfurtData:
    dict_elems = ["isin", "slug", "name", "performance"]

    def __init__(self) -> None:
        pass

    @classmethod
    def from_data(cls, isin, info_data, performance_data) -> "FrankfurtData":
        obj = cls()
        obj.isin = isin
        obj.slug = info_data["slug"]
        obj.name = info_data["name"]["originalValue"]
        obj.performance = performance_data
        return obj

    @classmethod
    def from_dict(cls, d: dict) -> "FrankfurtData":
        obj = cls()
        for elem in cls.dict_elems:
            setattr(obj, elem, d[elem])
        return obj

    def to_dict(self) -> dict:
        def inner():
            for elem in self.dict_elems:
                yield elem, getattr(self, elem)

        return dict(inner())
    
    def __repr__(self) -> str:
        return f"<FrankfurtData isin={self.isin} slug={self.slug} name={self.name} performance={self.performance}>"


class FrankfurtDataEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FrankfurtData):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)


class FrankfurtDataDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, d: dict[str, Any]) -> Any:
        if FrankfurtData.dict_elems == list(d.keys()):
            return FrankfurtData.from_dict(d)
        return d


def fetchen_wir(isins, timeout=3, headless=True, debug=True):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")

    not_found_on_ex = []
    data = {}
    with webdriver.Chrome(options=opts) as driver:
        driver.execute_cdp_cmd("Performance.enable", {})
        driver.get("https://www.boerse-frankfurt.de/")
        inp = driver.find_element(By.CSS_SELECTOR, "#mat-input-0")
        todo = len(isins)
        print(f"todo: {todo}")
        max_req_time = 0
        req_times = 0
        req_times_n = 0
        avg_req_time = 0
        info_data = None
        for i in range(todo):
            isin = isins[i]
            data_not_available = False
            print(f"\r#{todo}", end=" ", flush=True)
            while True:
                inp.clear()
                inp.send_keys(isin)
                starttime = time.time()
                try:
                    info_request = driver.wait_for_request(
                        f"de\?searchTerms={isin}", timeout=timeout
                    )
                    # """https://api.boerse-frankfurt.de/v1/global_search/limitedsearch/de?searchTerms=IE00B1FZS798"""
                    reqtime = time.time() - starttime
                    req_times += reqtime
                    req_times_n += 1
                    decompressed = gzip.decompress(info_request.response.body)
                    info_data = json.loads(decompressed)
                    # print(info_request.method)
                    # print(isin, decompressed)
                    if not info_data:
                        data_not_available = True
                    else:
                        info_data = info_data[0][0]
                    break
                    # print(info_data)
                    # print(info_request.__dict__)

                    """
                    {
                        "isin": "IE00B8KGV557",
                        "slug": "ishares-edge-msci-em-minimum-volatility-ucits-etf-usd-acc",
                        "wkn": null,
                        "symbol": null,
                        "investmentCompany": null,
                        "issuer": null,
                        "type": "ETP",
                        "typeName": {
                            "originalValue": "ETP",
                            "translations": {}
                        },
                        "count": 112,
                        "name": {
                            "originalValue": "iShares Edge MSCI EM Minimum Volatility UCITS ETF USD (Acc)",
                            "translations": {}
                        }
                    }
                    """

                except TimeoutException:
                    req_times += timeout
                    req_times_n += 1
                    continue
            if data_not_available:
                not_found_on_ex.append(isin)
                continue
            inp.send_keys(Keys.RETURN)
            starttime = time.time()
            try:
                performance_request = driver.wait_for_request(
                    f"/data/performance\?isin={isin}", timeout=timeout
                )
                reqtime = round(time.time() - starttime, 3)
                req_times += reqtime
                req_times_n += 1
                todo -= 1
                if reqtime > max_req_time:
                    max_req_time = reqtime
                if max_req_time > avg_req_time:  # optimize the timeout
                    timeout = math.ceil(max_req_time)
                performance_data = json.loads(
                    gzip.decompress(performance_request.response.body)
                )
                # performance_data["isin"] = isin
                if "isin" in performance_data:
                    del performance_data["isin"]

                data_obj = FrankfurtData.from_data(isin, info_data, performance_data)
                yield data_obj
                data[isin] = data_obj
                if debug:

                    def log():
                        if performance_data["years1"]:
                            log_data = performance_data["years1"]["changeInPercent"]
                            if log_data:
                                print(
                                    isin,
                                    f"{round(log_data, 1)}%",
                                    f"(remaining: {datetime.timedelta(seconds=math.ceil(avg_req_time * todo))}, timeout: {timeout})",
                                    end="    ",
                                    flush=True,
                                )

                    log()
            except TimeoutException:
                todo -= 1
                not_found_on_ex.append(isin)
                req_times += timeout
                req_times_n += 1
            avg_req_time = round(req_times / req_times_n, 3)

        print("max req time:", max_req_time)
        print("timeout:", timeout)
        print(len(not_found_on_ex), "isins were not found")
        frankfurt_data_file.write_text(json.dumps(data, cls=FrankfurtDataEncoder))
        driver.quit()


def isValid_ISIN_Code(str):
    # Regex to check valid ISIN Code
    # regex = "^[A-Z]{2}[-]{0, 1}[0-9A-Z]{8}[-]{0, 1}[0-9]{1}$"
    regex = "([A-Z]{2})([A-Z0-9]{9})([0-9]{1})"

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if str == None:
        return False

    # Return if the string
    # matched the ReGex
    if re.search(p, str):
        return True
    else:
        return False


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


def data_generator(n: int = -1) -> Generator[FrankfurtData, None, None]:
    if not isins_data_file.exists():
        if not etfs_pdf_file.exists() or not etfs_txt_file.exists():
            get_this_shit()
        da_parsen_wir_rein(keep=True)
    
    isins = isins_data_file.read_text().split("\n")
    n = min(n, len(isins))
    isins = isins[:n]
    isins_not_stored = []
    if frankfurt_data_file.exists():
        frankfurt_data_store = json.loads(
            frankfurt_data_file.read_text(), cls=FrankfurtDataDecoder
        )
        for isin in isins:
            if isin not in frankfurt_data_store:
                isins_not_stored.append(isin)
            else:
                # print(frankfurt_data_store[isin])
                yield frankfurt_data_store[isin]
    else:
        isins_not_stored = isins
    yield from fetchen_wir(isins_not_stored)


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