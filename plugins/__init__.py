import inspect
from base import Metric
from fierro_accounting import *
from fierro_sales import *
from calculated import *
from file import *
from query import *
from google import *


def get_metric_class(type_name):
    for klass in globals().values():
        if inspect.isclass(klass) and issubclass(klass, Metric) and klass.metric_type == type_name:
            return klass
