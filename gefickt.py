import json 
import requests as rq
import os 
import re 

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
    result = []
    etf = lambda isin: {"isin": isin}
    pages = text.strip().split("SPARPLAN-UNIVERSUM DEUTSCHLAND")[:-1]
    
    shitty_regex = re.compile(r"([A-Z]{2})([A-Z0-9]{9})([0-9]{1})", re.M)
    for page_number in range(len(pages)):
        page = pages[page_number]     
        for match in shitty_regex.findall(page):
            result.append(etf("".join(match)))
    open("etfs.json", "w").write(json.dumps(result, indent=4))
    print(f"{len(result)} etf results")
    # os.remove("etfs.pdf")



def fetchen_wir():
    # token = "64db7b5f34c448.48923483"
    # api = lambda isin: f"https://eodhistoricaldata.com/api/search/{isin}?api_token={token}"

    def api(isin):
        url = 'https://query1.finance.yahoo.com/v1/finance/search'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
        }

        params = dict(
            q=isin,
            quotesCount=1,
            newsCount=0,
            listsCount=0,
            quotesQueryId='tss_match_phrase_query'
        )
        return {"url": url, "headers": headers, "params": params}

    jj: list = json.loads(open("etfs.json", "r").read())
    items_to_process = len(jj)
    max_items_per_request = 500
    
    print(f"{items_to_process} items to process")
    print(f"{max_items_per_request} max items per rq")

    request_list = []

    etf_chunk_to_isin_chunk = lambda etf: etf['isin'] 

    while items_to_process > max_items_per_request: 
        start = items_to_process-max_items_per_request
        etf_chunk = jj[start:items_to_process]
        items_to_process = start
        request_list.append(api(",".join(map(etf_chunk_to_isin_chunk, etf_chunk))))
    if items_to_process > 0:
        print("remainder", items_to_process)
        request_list.append(api(",".join(map(etf_chunk_to_isin_chunk, jj[:items_to_process]))))
        
    print(f"built {len(request_list)} requests")

    def get_api(request):
        r = rq.get(**request).json()
        for x in r['quotes']:
            print(x['longname'], x['symbol'])
            # break
        return r

    r = get_api(request_list[0])
    print(r)
    # for etf in jj: 
    #     r = rq.get(api(etf['isin']))
    #     print(r.json())
    #     break


# get_this_shit()
da_parsen_wir_rein()
# fetchen_wir()