from dataclasses import dataclass
import requests as rq
import time 
from enum import Enum

class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class ProxyProvider:
    url: str
    type: ProxyType

    def pips(self):
        return rq.get(self.url).text.splitlines()

    def generator(self, timeout=10):
        pips = self.pips()
        print(f"checking {len(pips)} {self.type.value} proxies")
        this_ip = rq.get("https://ipv4.icanhazip.com/").text
        for pip in pips:
            try:
                starttime = time.time()
                proxy_ip = rq.get(
                    "https://ipv4.icanhazip.com/",
                    proxies={"http": f"{self.type.value}://{pip}", "https": f"{self.type.value}://{pip}"},
                    timeout=timeout,
                ).text
                assert proxy_ip != this_ip
            except Exception as e:
                pass
            else:
                request_time = round(time.time() - starttime, 3)
                print("found proxy", pip, "request time: ", request_time, "s")
                yield pip, request_time
    
    @classmethod
    def from_json(cls, json):
        return cls(json["url"], ProxyType(json["type"]))
    
    def to_json(self):
        return {"url": self.url, "type": self.type.value}



providers = [
    ProxyProvider(
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt",
        ProxyType.SOCKS4,
    ),
    ProxyProvider(
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt",
        ProxyType.SOCKS5,
    ),
]
def collect_providers(types=[ProxyType.SOCKS4, ProxyType.SOCKS5]):
    from itertools import chain
    return chain(*[provider.generator() for provider in providers if provider.type in types])
