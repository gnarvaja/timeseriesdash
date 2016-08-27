from plugins.base import Metric
from utils import ensure_date, generate_date_series
import csv


class CsvMetric(Metric):
    metric_type = "csv"

    def generate(self, ffrom, tto):
        period_type = self.get_period_type()
        file_name = self.config["filename"]
        date_column = self.config.get("date_column", 0)
        data_column = self.config.get("data_column", 1)
        filter_column = self.config.get("filter_column", -1)
        filter_value = self.config.get("filter_value", "")
        skip_rows = self.config.get("skip_rows", 0)

        f = csv.reader(open(file_name))

        if filter_column >= 0:
            def filter_row(r):
                return r[filter_column] == filter_value
        else:
            def filter_row(r):
                return True

        data = dict((ensure_date(row[date_column]), float(row[data_column]))
                    for i, row in enumerate(f)
                    if i >= skip_rows and row[date_column] and filter_row(row))

        return [{"label": d.strftime("%Y-%m-%d"), "data": data.get(d, 0)}
                for d in generate_date_series(ffrom, tto, period_type)]
