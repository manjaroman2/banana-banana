import requests as rq
import re 
from pathlib import Path 
import json 
import stat 
import time 
import datetime
import gzip
import math 


base_dir = Path(__file__).resolve().parent
data_dir = base_dir / "data"
tmp_dir = base_dir / "tmp"
update_geckodriver_script_file = tmp_dir / "update_geckodriver.sh"

if not data_dir.is_dir():
    data_dir.mkdir()
if not tmp_dir.is_dir():
    tmp_dir.mkdir()


def create_geckodriver_update_script():
    geckodriver_tar = tmp_dir / 'geckodriver.tar.xz'
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
    update_geckodriver_script_file.chmod(update_geckodriver_script_file.stat().st_mode | stat.S_IEXEC)


def update_geckodriver():
    if not update_geckodriver_script_file.exists():
        create_geckodriver_update_script()
    from subprocess import Popen, PIPE

    session = Popen(['bash', update_geckodriver_script_file.as_posix()], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()

    if stderr:
        raise Exception("Error "+str(stderr))
    
    print(str(stdout))

def fetchen_wir(timeout=2):
    
    isins = (data_dir / "isins").read_text().split("\n")
    from seleniumwire import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless=new')
    
    not_found_on_ex = []
    data = {}
    with webdriver.Chrome(options=opts) as driver:
        driver.execute_cdp_cmd('Performance.enable', {})
        driver.get("https://www.boerse-frankfurt.de/")
        inp = driver.find_element(By.CSS_SELECTOR, "#mat-input-0")
        todo = len(isins)
        print(f"todo: {todo}")
        max_req_time = 0
        req_times = 0
        req_times_n = 0
        avg_req_time = 0
        for i in range(todo): 
            isin = isins[i]
            while True:
                inp.send_keys(isin)
                try: 
                    driver.wait_for_request(f'/global_search/limitedsearch/de\?searchTerms={isin}', timeout=10)
                    break
                except TimeoutException: 
                    continue
            inp.send_keys(Keys.RETURN)
            starttime = time.time()
            try:
                performance_request = driver.wait_for_request(f'/data/performance\?isin={isin}', timeout=timeout)
                reqtime = round(time.time() - starttime, 3)
                req_times += reqtime
                req_times_n += 1
                todo -= 1
                avg_req_time = round(req_times / req_times_n, 3)
                if reqtime > max_req_time:
                    max_req_time = reqtime
                performance_data = json.loads(gzip.decompress(performance_request.response.body))
                data[isin] = performance_data
                print(f'\r#{todo}', isin, f"{round(performance_data['years1']['changeInPercent'], 1)}%", f"(remaining: {datetime.timedelta(seconds=math.ceil(avg_req_time * todo))})", end='    ', flush=True)
            except TimeoutException as e: 
                # print(f"ISIN {isin} not found on frankfurt")
                not_found_on_ex.append(isin)
                
        print("max req time:", max_req_time)
        print("timeout:", timeout)
        print(len(not_found_on_ex), "ISINS were not found")
        (data_dir / 'performance_data.json').write_text(json.dumps(data))
    

def isValid_ISIN_Code(str):
 
    # Regex to check valid ISIN Code
    # regex = "^[A-Z]{2}[-]{0, 1}[0-9A-Z]{8}[-]{0, 1}[0-9]{1}$"
    regex = "([A-Z]{2})([A-Z0-9]{9})([0-9]{1})"
 
    # Compile the ReGex
    p = re.compile(regex)
 
    # If the string is empty
    # return false
    if (str == None):
        return False
 
    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False

def get_this_shit():
    from pdfminer.high_level import extract_text

    der_link = "https://assets.traderepublic.com/assets/files/Sparplan-Universum.pdf"

    print(f"getting {der_link}")
    open("etfs.pdf", 'wb').write(rq.get(der_link).content)
    print("extracting text")
    text = extract_text("etfs.pdf")
    open("etfs.txt", "w").write(text)


def da_parsen_wir_rein():
    text = open("etfs.txt", "r").read()
    isins = []    
    pages = text.strip().split("SPARPLAN-UNIVERSUM DEUTSCHLAND")[:-1]
    shitty_regex = re.compile(r"([A-Z]{2})([A-Z0-9]{9})([0-9]{1})", re.M)
    for page_number in range(len(pages)):
        page = pages[page_number]     
        for match in shitty_regex.findall(page):
            isin = "".join(match)
            isins.append(isin)
    (data_dir / "isins").write_text("\n".join(isins))
    print(f"{len(isins)} etf results")
    # os.remove("etfs.pdf")


# get_this_shit()
# da_parsen_wir_rein()
# update_geckodriver()
fetchen_wir()


# t = driver.execute_cdp_cmd('Performance.getMetrics', {})
# print(t)
# driver.execute_cdp_cmd('Network.getResponseBody')

# def process_browser_log_entry(entry):
#     response = json.loads(entry['message'])['message']
#     return response

# logs = driver.get_log("performance")
# print(logs)
# events = [process_browser_log_entry(entry) for entry in browser_log]
# driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': events[0]["params"]["requestId"]})
# events = [event for event in events if 'Network.response' in event['method']]
# fetchen_wir()


# import nasdaqdatalink
# mydata = nasdaqdatalink.get("FRED/GDP")
# print(mydata)