from plugins.base import Metric
from utils import ensure_date, generate_date_series
import csv


class CsvMetric(Metric):
    metric_type = "csv"

    def generate(self, ffrom, tto):
        period_type = self.config["period"]
        file_name = self.config["filename"]
        date_column = self.config.get("date_column", 0)
        data_column = self.config.get("data_column", 1)

        f = csv.reader(open(file_name))

        data = dict((ensure_date(row[date_column]), float(row[data_column]))
                    for row in f if row[date_column])

        return [{"label": d.strftime("%Y-%m-%d"), "data": data.get(d, 0)}
                for d in generate_date_series(ffrom, tto, period_type)]
