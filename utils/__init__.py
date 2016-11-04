# -*- coding: utf-8 -*-
import datetime
import json
import os
from six import string_types
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse, parserinfo


def _get_metric(metric_name, config):
    ret = [m for m in get_metrics(config) if m["name"] == metric_name]
    if ret:
        return ret[0]


def _get_data_dir(metric_name, config):
    metric = _get_metric(metric_name, config)
    if not metric:
        raise RuntimeError("Metric %s not found" % metric_name)
    if metric.get("visible", True):
        data_dir = config["data_dir"]
    else:
        data_dir = config.get("hidden_data_dir", config["data_dir"])
    return data_dir


def save_data(data, metric_name, config):
    data_dir = _get_data_dir(metric_name, config)
    json_filename = os.path.join(data_dir, metric_name + ".json")
    json.dump(data, open(json_filename, "wt"), indent=2)


def read_data(metric_name, config):
    data_dir = _get_data_dir(metric_name, config)
    json_filename = os.path.join(data_dir, metric_name + ".json")
    if not os.path.exists(json_filename):
        return []
    return json.load(open(json_filename))


def get_metric_names(global_config):
    "Devuelve la lista de todas las métricas disponibles"
    return [m["name"] for m in get_metrics(global_config)]


def expand_template(metric, template):
    params = dict(template.get("defaults", {}))
    aux = dict(metric)
    del aux["template"]
    params.update(aux)
    for m in template["metrics"]:
        new_metric = dict(m)
        for k, v in new_metric.items():
            # Reemplazo $parametro por el valor
            for param_name, param_value in params.items():
                param_marker = "$" + param_name
                if isinstance(v, str) and param_marker in v:
                    v = v.replace(param_marker, param_value)
            new_metric[k] = v
        yield new_metric


def get_metrics(global_config):
    ret = []
    for metric in global_config["metrics"]:
        if "template" in metric:
            template = [t for t in global_config["metric-templates"] if t["name"] == metric["template"]]
            if not template or len(template)>1:
                raise RuntimeError("Metric Template %s not found" % metric["template"])
            template = template[0]
            ret.extend(expand_template(metric, template))
        else:
            ret.append(metric)
    return ret


def generate_date_series(ffrom, tto, period):
    """
    Genera series desde `ffrom` hasta `tto` para el `period`

    >>> list(generate_date_series(datetime.date(2015, 1, 1), \
                                      datetime.date(2015, 3, 31), "month"))
    [datetime.date(2015, 1, 1), datetime.date(2015, 2, 1), \
datetime.date(2015, 3, 1)]
    >>> list(generate_date_series(datetime.date(2015, 1, 1), \
                                      datetime.date(2015, 1, 20), "week"))
    [datetime.date(2015, 1, 1), datetime.date(2015, 1, 8), \
datetime.date(2015, 1, 15)]
    """
    delta = get_delta(period)
    if period == "month":
        ffrom = date_to_period(period, ffrom)
    yield ensure_date(ffrom)
    while True:
        ffrom += delta
        if ffrom > tto:
            break
        yield ensure_date(ffrom)


def get_delta(period):
    if period == "month":
        delta = relativedelta(months=1)
    elif period == "week":
        delta = relativedelta(weeks=1)
    elif period == "day":
        delta = relativedelta(days=1)
    elif period == "year":
        delta = relativedelta(years=1)
    return delta


def calculate_period_to(ffrom, period):
    return ffrom + get_delta(period) - relativedelta(days=1)


class _SpanishParserInfo(parserinfo):
    MONTHS = [(u'Ene', u'Enero'),
              (u'Feb', u'Febrero'),
              (u'Mar', u'Marzo'),
              (u'Abr', u'Abril'),
              (u'May', u'Mayo'),
              (u'Jun', u'Junio'),
              (u'Jul', u'Julio'),
              (u'Ago', u'Agosto'),
              (u'Sep', u'Sept', u'Septiembre', u'Setiembre'),
              (u'Oct', u'Octubre'),
              (u'Nov', u'Noviembre'),
              (u'Dec', u'Diciembre')]
    WEEKDAYS = [(u'Lun', u'Lunes'),
                (u'Mar', u'Martes'),
                (u'Mie', u'Mié', u'Miércoles', u'Miercoles'),
                (u'Jue', u'Jueves'),
                (u'Vie', u'Viernes'),
                (u'Sáb', u'Sab', u'Sábado', u'Sabado'),
                (u'Dom', u'Domingo')]


def ensure_date(x):
    if isinstance(x, datetime.datetime):
        return x.date()
    elif isinstance(x, datetime.date):
        return x
    elif isinstance(x, string_types):
        default = datetime.datetime.now().replace(day=1)  # Si no está especificado el día toma el 1ero
                                                          # Si no está mes u año, toma los actuales
        try:
            return parse(x, default=default).date()
        except ValueError:
            return parse(x, _SpanishParserInfo(), default=default).date()
    raise ValueError("Expected date or datetime")


def parse_float(x):
    """
    Convierte a float cualquier string
    >>> parse_float(1)
    1.0
    >>> parse_float("1.123.123,55")
    1123123.55
    >>> parse_float("123123,55")
    123123.55
    >>> parse_float("123.123")
    123123.0
    >>> parse_float("123.12")
    123.12
    >>> parse_float("123 %")
    1.23
    """
    if isinstance(x, string_types):
        x = x.replace("$", "").strip()
        if "%" in x:
            return parse_float(x.replace("%", "")) / 100.0
        if "." in x and "," in x:
            if x.index(",") < x.index("."):
                # , es el separador de miles y . de decimales
                return float(x.replace(",", ""))
            else:
                return float(x.replace(".", "").replace(",", "."))
        elif "," in x:
            if (len(x.replace(",", "")) - len(x)) > 1 or x[-4] == ",":
                return float(x.replace(",", ""))  # Considero que es separador de miles
            else:  # Es separador de decimales
                return float(x.replace(",", "."))
        elif "." in x:
            if (len(x.replace(".", "")) - len(x)) > 1 or x[-4] == ".":
                return float(x.replace(".", ""))  # Considero que es separador de miles
            else:  # Es separador de decimales
                return float(x)
        else:
            return float(x)
    else:
        return float(x)


def date_to_period(period_type, date):
    if period_type == "day":
        return date
    elif period_type == "month":
        return date.replace(day=1)
    elif period_type == "week":
        return date - datetime.timedelta(days=date.weekday())


def accumulate(totalized_movs, sum_type):
    """Acumula los totales de acuerdo a sum_type

    >>> data = [(datetime.date(2015, 11, 1), 10), \
                    (datetime.date(2015, 12, 1), 15), \
                    (datetime.date(2016, 1, 1), 25), \
                    (datetime.date(2016, 2, 1), 30),]
    >>> accumulate(list(data), "sum")[-1][1]
    30
    >>> accumulate(list(data), "accum")[-1][1]
    80
    >>> accumulate(list(data), "accum_year_reset")[-1][1]
    55
    >>> accumulate(list(data), "accum_year_reset")[-2][1]
    25
    >>> accumulate(list(data), "accum_year_reset")[-3][1]
    25
    """
    if sum_type in ("accum", "accum_year_reset"):
        for i, row in enumerate(totalized_movs):
            if i == 0:
                continue
            if sum_type == "accum_year_reset" and row[0].year != totalized_movs[i - 1][0].year:
                continue  # Reset each new year
            totalized_movs[i] = (row[0], row[1] + totalized_movs[i - 1][1])
    return totalized_movs
