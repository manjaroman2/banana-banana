import requests 
import json 
def get_symbol_for_isin(isins):
    url = 'https://query1.finance.yahoo.com/v1/finance/search'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
    }

    params = dict(
        q=",".join(isins),
        quotesCount=len(isins),
        newsCount=0,
        listsCount=0,
        quotesQueryId='tss_match_phrase_query'
    )

    resp = requests.get(url=url, headers=headers, params=params)
    # print(resp.content)
    data = resp.json()
    if 'quotes' in data and len(data['quotes']) > 0:
        return [{"yahoo_symbol": r['symbol'], "yahoo_longname": r["longname"]} for r in data['quotes']]
    else:
        return None

def populate_yahoo_symbols():
    jj = json.loads(open("etfs.json", "r").read())
    isins = [e['isin'] for e in jj]
    n = 20
    print(jj[:n])
    
    r = get_symbol_for_isin(list(reversed(isins[:n])))
    print(r)
    for i in range(n):
        etf = jj[i] | r[i]
        print(etf)
    # for e in jj:
    #     e["yahoo_symbol"] = 
    #     print(e)
    open("etfs.json", "w").write(json.dumps(jj, indent=4))


# populate_yahoo_symbols()
import yfinance
r = yfinance.download("EMMV.LSE")
print(r)