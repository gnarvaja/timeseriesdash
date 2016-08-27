# -*- coding: utf-8 -*-
import re
import keyword
import string
import parser
import math  # noqa
from plugins.base import Metric
from utils import read_data, get_metric_names, ensure_date


def extract_variables(expression):
    """
    Extrae las variables de una expresión

    >>> extract_variables("a+1")
    ['a']

    >>> extract_variables("a+b")
    ['a', 'b']

    >>> extract_variables("b + a")
    ['a', 'b']

    >>> extract_variables("math.sqrt + a")
    ['a', 'math']

    """

    expr = parser.expr(expression)

    def _extract_variables(list_):
        for elem in list_:
            if isinstance(elem, list):
                _extract_variables(elem)
            elif isinstance(elem, str):
                if elem and (elem[0] in string.ascii_letters or elem[0] == "_") and \
                        elem not in keyword.kwlist:
                    ret.append(elem)

    ret = []
    _extract_variables(expr.tolist())
    # Elimina lo que sean métodos
    ret = [var for var in ret if "." + var not in expression]
    return sorted(ret)


class CalculatedMetric(Metric):
    metric_type = "calculated"

    builtin_variables = ["math"]

    def __init__(self, *args, **kargs):
        super(CalculatedMetric, self).__init__(*args, **kargs)
        self.formula = self.config["formula"]
        self.variables = extract_variables(self.config["formula"])
        self.zero_division_default = self.config.get("zero_division_default", None)

    def _add_builtin_variables(self, eval_vars):
        for var in self.variables:
            if var in self.builtin_variables:
                eval_vars[var] = globals()[var]

    def generate(self, ffrom, tto):
        eval_vars = {}

        self._add_builtin_variables(eval_vars)

        datas = {}
        data_len = None
        for var in self.variables:
            if var in self.builtin_variables:
                continue
            datas[var] = read_data(var, self.global_config)
            if data_len is None:
                data_len = len(datas[var])
            elif data_len != len(datas[var]):
                raise RuntimeError("Error la longitud de los datos de la variable %s"
                                   " no coincide con las precedentes" % var)

        formula = compile(self.formula, self.name, "eval")
        data = []
        for i in range(data_len):
            var_names = datas.keys()
            labels = set(datas[v][i]["label"] for v in var_names)
            if len(labels) > 1:
                raise RuntimeError("Labels distintos para valor %s - %s" % (i, labels))

            label = list(labels)[0]
            for var in var_names:
                eval_vars[var] = datas[var][i]["data"]

            try:
                d = eval(formula, eval_vars)
            except ZeroDivisionError:
                if self.zero_division_default is None:
                    raise
                else:
                    d = self.zero_division_default
            data.append({"label": label, "data": d})

        return data


class AggregateMetric(Metric):
    metric_type = "aggregate"

    def generate(self, ffrom, tto):
        aggregate_type = self.config.get("aggregate_type", "average")
        variables = self.config["variables"].split(",")
        variables_new = []
        for var in variables:
            if [x for x in var if x not in (string.ascii_letters + "_")]:
                # No es una variable, supongo que es una expresión regular.
                try:
                    var_re = re.compile(var)
                except:
                    raise RuntimeError("'%s' no es una variable válida y tampoco una expresión regular" % var)
                variables_new.extend([n for n in get_metric_names(self.global_config) if var_re.match(n)])
            else:
                variables_new.append(var)

        datas = {}
        data_len = None
        data = []
        for var in variables_new:
            datas[var] = read_data(var, self.global_config)
            if data_len is None:
                data_len = len(datas[var])
            elif data_len != len(datas[var]):
                raise RuntimeError("Error la longitud de los datos de la variable %s"
                                   " no coincide con las precedentes" % var)
        initial = 1.0
        for i in range(data_len):
            var_names = datas.keys()
            labels = set(datas[v][i]["label"] for v in var_names)
            if len(labels) > 1:
                raise RuntimeError("Labels distintos para valor %s - %s" % (i, labels))

            label = list(labels)[0]
            if aggregate_type == "average":
                d = sum([datas[v][i]["data"] for v in var_names]) / float(len(var_names))
            elif aggregate_type == "sum":
                d = sum([datas[v][i]["data"] for v in var_names])
            elif aggregate_type == "percent_accum":
                # Acumula porcentajes
                d = initial * (1.0 + datas[var_names[0]][i]["data"])
                initial = d
            elif aggregate_type == "count":
                d = len(var_names)
            data.append({"label": label, "data": d})

        return data


class RebaseMetric(Metric):
    """Nueva métrica a partir de transformar a otra en base 100 (o el número que sea)

       Si no se indica base_pivot, se toma el primer valor.

       Ejemplo si la serie es: [23, 46, 120], y se toma como pivot el primer valor, el resultante es
       [100, 200, 521.739]
    """

    metric_type = "rebase"

    def generate(self, ffrom, tto):
        source = self.config["source"]
        base = float(self.config.get("base", 100))
        source_data = read_data(source, self.global_config)
        if "base_pivot" in self.config:
            base_pivot = self.config["base_pivot"]
            pivot = [d["data"] for d in source_data if ensure_date(d["label"]) == base_pivot]
            if not pivot:
                raise RuntimeError("Pivot value for base_pivot = %s not found" % base_pivot)
            pivot = pivot[0]
        else:
            pivot = source_data[0]["data"]

        ret = [{'label': it["label"], 'data': it["data"] * base / pivot} for it in source_data]
        return ret
