import inspect
from .base import Metric
from .fierro_accounting import *  # noqa
from .fierro_sales import *  # noqa
from .calculated import *  # noqa
from .file import *  # noqa
from .query import *  # noqa
from .google import *  # noqa
from .affise import *  # noqa


def get_metric_class(type_name):
    for klass in globals().values():
        if inspect.isclass(klass) and issubclass(klass, Metric) and klass.metric_type == type_name:
            return klass
