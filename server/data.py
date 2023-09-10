from dataclasses import dataclass
import abc
import json


to_csv = {str: lambda x: x, dict: lambda x: json.dumps(x)}
from_csv = {str: lambda x: x, dict: lambda x: json.loads(x)}


class DataHandler(abc.ABC):
    @property
    @abc.abstractmethod
    def dict_elems(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def info_data_type_to_slug(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def possible_timespans(self):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_data(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d: dict) -> "DataHandler":
        obj = cls()
        for elem in cls.dict_elems.keys():
            setattr(obj, elem, d[elem])
        return obj

    def to_dict(self) -> dict:
        def inner():
            for elem in self.dict_elems.keys():
                yield elem, getattr(self, elem)

        return dict(inner())

    @classmethod
    def from_csv(cls, l: list) -> "DataHandler":
        obj = cls()
        for k, v in cls.dict_elems.items():
            setattr(obj, k, from_csv[v](l.pop(0)))
        return obj

    def to_csv(self) -> list:
        def inner():
            for k, v in self.dict_elems.items():
                yield to_csv[v](getattr(self, k))

        return list(inner())

    def __repr__(self) -> str:
        def inner():
            for k in self.dict_elems.keys():
                yield f"{k}={getattr(self, k)}"

        return "<{} {}>".format(self.__class__.__name__, " ".join(inner()))


class FrankfurtData(DataHandler):
    dict_elems = {"isin": str, "slug": str, "name": str, "performance": dict}
    info_data_type_to_slug = {"ETP": "etf", "EQUITY": "aktie"}
    possible_timespans = ["months1", "months3", "months6", "years1", "years2", "years3"]

    @classmethod
    def from_data(cls, isin, info_data, performance_data) -> "FrankfurtData":
        obj = cls()
        obj.isin: str = isin
        obj.slug: str = (
            cls.info_data_type_to_slug[info_data["type"]] + "/" + info_data["slug"]
        )
        obj.name: str = info_data["name"]["originalValue"]
        obj.performance: dict = performance_data
        return obj


from flask import Response
def jsonify(d):
    return Response(
        json.dumps(d, cls=FrankfurtDataEncoder), mimetype="application/json"
    )


@dataclass
class Provider:
    name: str
    css_input_selector: str
    url: str
    search_param: str
    data_search_param: str
    data_handler: DataHandler


class Providers:
    frankfurt = Provider(
        "frankfurt",
        "input.mat-input-element",
        "https://www.boerse-frankfurt.de/",
        f"de\?searchTerms=",
        "performance",
        FrankfurtData,
    )
    # wallstreet = Provider("wallstreet", "#search", "https://www.wallstreet-online.de/", "searchInst")


class FrankfurtDataEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, FrankfurtData):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)


class FrankfurtDataDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, d: dict):
        if list(FrankfurtData.dict_elems.keys()) == list(d.keys()):
            return FrankfurtData.from_dict(d)
        return d
