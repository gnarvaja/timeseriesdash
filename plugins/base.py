import random
from utils.db import DBFactory
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
from utils import read_data, generate_date_series

COLORS = ["primary", "green", "red", "yellow", "cyan", "orange", "brown"]


class Metric(object):
    metric_type = "base"

    def __init__(self, global_config, config, name):
        self.global_config = global_config
        self.config = config
        self.name = name

    def generate(self, ffrom, tto):
        raise NotImplementedError()

    def get_period_type(self):
        return getattr(self, "period_type",
                       self.config.get("period_type",
                                       self.global_config.get("default_period_type", "month")))

    def js_line(self):
        if not self.config.get("visible", True):
            return ""
        template = '    new Metric("%(visible_name)s", "%(icon)s", "%(name)s", "%(color)s", "%(period_type)s"),\n'
        return template % {
            "name": self.name,
            "visible_name": self.config.get("visible_name", self.name),
            "icon": self.config.get("icon", "bar-chart"),
            "color": self.config.get("color", random.choice(COLORS)),
            "period_type": self.get_period_type()
        }

    def _reused_data(self, ffrom, tto):
        reuse = self.config.get("reuse", False)
        period_type = self.get_period_type()
        if reuse:
            old_data = read_data(self.name, self.global_config)
            ret = dict((parse_date(v["label"]).date(), v["data"]) for v in old_data)
            missing_dates = [d for d in generate_date_series(ffrom, tto, period_type)
                             if not d in ret]
            if not missing_dates:
                return old_data, None, None
            new_ffrom = missing_dates[0]
            new_tto = missing_dates[-1] + relativedelta(**{"%ss" % period_type: 1}) - relativedelta(days=1)
        else:
            new_ffrom = ffrom
            new_tto = tto
            ret = {}
        return ret, new_ffrom, new_tto


class DBMetric(Metric):
    def __init__(self, *args, **kargs):
        super(DBMetric, self).__init__(*args, **kargs)
        dbname = self.config.get("database", self.global_config.get("default_database"))
        self.db = DBFactory.get_db(self.global_config, dbname)

