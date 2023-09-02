# Copyright 2017 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import urllib.request
import urllib.parse

'''
See https://www.openfigi.com/api for more information.
'''

openfigi_apikey = ''  # Put API Key here
jobs = [
    {'idType': 'ID_ISIN', 'idValue': 'US4592001014'},
    {'idType': 'ID_WERTPAPIER', 'idValue': '851399', 'exchCode': 'US'},
    {'idType': 'ID_BB_UNIQUE', 'idValue': 'EQ0010080100001000', 'currency': 'USD'},
    {'idType': 'ID_SEDOL', 'idValue': '2005973', 'micCode': 'EDGX', 'currency': 'USD'}
]


def map_jobs(jobs):
    '''
    Send an collection of mapping jobs to the API in order to obtain the
    associated FIGI(s).

    Parameters
    ----------
    jobs : list(dict)
        A list of dicts that conform to the OpenFIGI API request structure. See
        https://www.openfigi.com/api#request-format for more information. Note
        rate-limiting requirements when considering length of `jobs`.

    Returns
    -------
    list(dict)
        One dict per item in `jobs` list that conform to the OpenFIGI API
        response structure.  See https://www.openfigi.com/api#response-fomats
        for more information.
    '''
    handler = urllib.request.HTTPHandler()
    opener = urllib.request.build_opener(handler)
    openfigi_url = 'https://api.openfigi.com/v2/mapping'
    request = urllib.request.Request(openfigi_url, data=bytes(json.dumps(jobs), encoding='utf-8'))
    request.add_header('Content-Type','application/json')
    if openfigi_apikey:
        request.add_header('X-OPENFIGI-APIKEY', openfigi_apikey)
    request.get_method = lambda: 'POST'
    connection = opener.open(request)
    if connection.code != 200:
        raise Exception('Bad response code {}'.format(str(response.status_code)))
    return json.loads(connection.read().decode('utf-8'))


def job_results_handler(jobs, job_results):
    '''
    Handle the `map_jobs` results.  See `map_jobs` definition for more info.

    Parameters
    ----------
    jobs : list(dict)
        The original list of mapping jobs to perform.
    job_results : list(dict)
        The results of the mapping job.

    Returns
    -------
        None
    '''
    for job, result in zip(jobs, job_results):
        job_str = '|'.join(job.values())
        r = result['data'][0]

        tickers = [e['ticker'] for e in result['data']]
        for e in result['data']:
            print(e)
        print(tickers)
        break
        ticker = ""
        i = len(result['data']) - 1
        while not ticker:
            if i == -1: 
                for e in result['data']:
                    if e['ticker'].endswith("EUR"):
                        ticker = e['ticker']
                        break
                else:
                    print(list(set([e['ticker'] for e in result['data']])))
                    raise Exception("dreck")
                break
            e = result['data'][i]
            if e['ticker'].endswith("USD"):
                ticker = e['ticker']
                break
            i -= 1 

        # tickers = list(set([ if x['ticker'].endswith("USD") or x['ticker'].endswith("EUR")]))
        print(job, ticker)
        # figis_str = ','.join([d['figi'] for d in result.get('data', [])])
        # result_str = figis_str or result.get('error')
        # output = '%s maps to FIGI(s) ->\n%s\n---' % (job_str, result_str)
        # print(output)


def main():
    '''
    Map the defined `jobs` and handle the results.

    Returns
    -------
        None
    '''
    job_results = map_jobs(jobs[:10])
    job_results_handler(jobs, job_results)

jj = json.loads(open("etfs.json", "r").read())
isin_job = lambda idvalue: {'idType': 'ID_ISIN', 'idValue': idvalue}
jobs = [isin_job(e['isin']) for e in jj]
print(len(jobs), "jobs")

main()