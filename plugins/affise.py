from urllib import parse
import requests
from plugins.base import Metric
from utils import generate_date_series, calculate_period_to


class AffiseMetric(Metric):
    metric_type = "affise"

    def __init__(self, *args, **kargs):
        super(AffiseMetric, self).__init__(*args, **kargs)
        affise_defaults = self.global_config.get("affise_defaults", {})
        self.base_url = self.config.get("base_url", affise_defaults.get("base_url"))
        self.base_url = self.base_url.rstrip("/")
        self.api_key = self.config.get("api_key", affise_defaults.get("api_key"))
        self.filters = self.config.get("filters", {})
        self.filter_format = self.config.get("filter_format", '{}')
        self.path = self.config["path"]
        if not self.path.startswith("/"):
            self.path = "/" + self.path
        self.limit = self.config.get("limit", 1)

    def generate(self, ffrom, tto):
        period_type = self.get_period_type()

        url = self.base_url + self.path

        params = {
            "limit": self.limit,
        }
        for k, v in self.filters.items():
            params[self.filter_format.format(k)] = v

        ret, new_ffrom, new_tto = self._reused_data(ffrom, tto)
        if new_ffrom is None and new_tto is None:  # full reuse - ret == old_data
            return ret

        for period_from in generate_date_series(new_ffrom, new_tto, period_type):
            period_to = calculate_period_to(period_from, period_type)

            period_params = dict(params)
            period_params.update({
                self.filter_format.format("date_from"): period_from.strftime("%Y-%m-%d"),
                self.filter_format.format("date_to"): period_to.strftime("%Y-%m-%d"),
            })

            resp = requests.get(url + "?{}".format(parse.urlencode(period_params)),
                                headers={"API-Key": self.api_key})

            resp.raise_for_status()
            resp = resp.json()

            ret[period_from] = resp["pagination"]["total_count"]

        totalized_movs = sorted(ret.items(), key=lambda k_v: k_v[0])

        data = [{"label": row[0].strftime("%Y-%m-%d"), "data": float(row[1])}
                for row in totalized_movs]
        return data
