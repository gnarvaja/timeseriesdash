# -*- coding: utf-8 -*-
"Script que sube las métricas a la planilla"
import datetime
import gspread
from plugins.base import Metric
from utils.oauth2 import OA2CredentialsFactory
from utils.ga_profile import GAProfilesFactory
from utils import ensure_date, generate_date_series, parse_float, date_to_period


class GoogleSpreadMetric(Metric):
    metric_type = "googlespread"

    def __init__(self, *args, **kargs):
        super(GoogleSpreadMetric, self).__init__(*args, **kargs)
        oa2_credentials = self.config.get("credentials", self.global_config.get("default_oa2_credentials"))
        self.credentials = OA2CredentialsFactory.get_credentials(self.global_config, oa2_credentials)
        self.spreadsheet = self.config.get("spreadsheet")
        self.sheet = self.config.get("sheet", "sheet1")

    def generate(self, ffrom, tto):
        gc = gspread.authorize(self.credentials)
        wks = getattr(gc.open(self.spreadsheet), self.sheet)

        period_type = self.get_period_type()

        ret, new_ffrom, new_tto = self._reused_data(ffrom, tto)
        if new_ffrom is None and new_tto is None:  # full reuse - ret == old_data
            return ret

        date_column = self.config.get("date_column", 1)
        data_column = self.config.get("data_column", 2)
        start_row = self.config.get("start_row", 0)

        data_values = wks.col_values(data_column)

        data = {}

        for i, v in enumerate(wks.col_values(date_column)):
            if i < start_row:
                continue
            if not v:
                continue
            data[ensure_date(v)] = parse_float(data_values[i] or "0")

        return [{"label": d.strftime("%Y-%m-%d"), "data": data.get(d, 0)}
                for d in generate_date_series(ffrom, tto, period_type)]


class GoogleAnalyticsMetric(Metric):
    metric_type = "googleanalytics"

    def __init__(self, *args, **kargs):
        super(GoogleAnalyticsMetric, self).__init__(*args, **kargs)
        profile_name = self.config.get("profile", self.global_config.get("default_ga_profile"))
        self.profile = GAProfilesFactory.get_profile(self.global_config, profile_name)
        self.metric_name = self.config.get("metric", self.config.get("name"))

    def generate(self, ffrom, tto):
        period_type = self.get_period_type()

        ret, new_ffrom, new_tto = self._reused_data(ffrom, tto)
        if new_ffrom is None and new_tto is None:  # full reuse - ret == old_data
            return ret
        values = self.profile.core.query.metrics(self.metric_name).daily(
            new_ffrom, days=(new_tto - new_ffrom).days + 1).values

        # Agrupo por período
        for i, v in enumerate(values):
            date = new_ffrom + datetime.timedelta(days=i)
            period_start = date_to_period(period_type, date)
            ret[period_start] = v + ret.get(period_start, 0)

        return [{"label": d.strftime("%Y-%m-%d"), "data": ret.get(d, 0)}
                for d in generate_date_series(ffrom, tto, period_type)]
