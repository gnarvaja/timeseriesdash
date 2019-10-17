#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import json
import sys
import os
import re
import yaml
import plugins
import codecs
from utils import save_data, get_metrics, read_data, get_metric_names
from utils.db import DBFactory
from utils.oauth2 import OA2CredentialsFactory
import gspread
from environs import Env

env = Env()

env.read_env(os.getenv("ENV_PATH") or None)


def upload(config, argv):
    credentials_name = argv[3]
    spreadsheet = argv[4]
#    sheet = argv[5]

    credentials = OA2CredentialsFactory.get_credentials(config, credentials_name)
    gc = gspread.authorize(credentials)
    wks = getattr(gc.open(spreadsheet), "sheet1")

    weeks = wks.row_values(3)
    metrics = wks.col_values(1)
    all_metrics = get_metric_names(config)

    cells = []

    for row, metric in enumerate(metrics):
        metric = metric.strip()
        if not metric:
            continue
        if metric not in all_metrics:
            print("WARNING: %s no se encuentra en las métricas" % metric)
            continue
        all_metrics.remove(metric)
        data = read_data(metric, config)
        print("uploading %s" % metric)
        for data_item in data:
            if not data_item["label"] in weeks:
                continue
            col = weeks.index(data_item["label"])
            #import ipdb; ipdb.set_trace()
            #wks.update_cell(row + 1, col + 1, data_item["data"])
            cell = wks.cell(row + 1, col + 1)
            cell.value = data_item["data"]
            cells.append(cell)

    wks.update_cells(cells)
    print("Métricas no subidas: %s" % all_metrics)


envvar_matcher = re.compile(r'\$\{([A-Za-z0-9_]+)(:-[^\}]*)?\}')


def envvar_constructor(loader, node):
    '''
    Extract the matched value, expand env variable, and replace the match
    ${REQUIRED_ENV_VARIABLE} or ${ENV_VARIABLE:-default}
    '''
    value = node.value
    match = envvar_matcher.match(value)
    env_var = match.group(1)
    default_value = match.group(2)
    if default_value is not None:
        return env.str(env_var, default_value[2:]) + value[match.end():]
    else:
        return env.str(env_var) + value[match.end():]


def main(argv):
    config_file = argv[1]

    yaml.add_implicit_resolver('!envvar', envvar_matcher, Loader=yaml.FullLoader)
    yaml.add_constructor('!envvar', envvar_constructor, Loader=yaml.FullLoader)
    config = yaml.load(open(config_file), Loader=yaml.FullLoader)

    if argv[2] == "upload":
        return upload(config, argv)

    ffrom = datetime.date(*map(int, argv[2].split("-")))
    tto = datetime.date(*map(int, argv[3].split("-")))
    extra_args = argv[4:]

    skip_metrics = "--skip-metrics" in extra_args

    js_metrics = codecs.open(config["js_metrics"], "w", encoding="utf-8")

    js_metrics.write("metrics = [\n")

    for metric in get_metrics(config):
        metric_class = plugins.get_metric_class(metric["type"])
        if not metric_class:
            print("Error no existe la métrica de tipo %s" % metric["type"], file=sys.stderr)
            sys.exit(3)
        metric_obj = metric_class(config, metric, metric["name"])
        if not skip_metrics:
            print("Generating metric %s" % metric["name"])
            data = metric_obj.generate(ffrom, tto)

            save_data(data, metric["name"], config)

        js_metrics.write(metric_obj.js_line())

    js_metrics.write("];\n")
    js_metrics.write("\n")
    js_metrics.write("\n")

    js_metrics.write("pills = [\n")
    for pill in config["pills"]:
        js_metrics.write("jQuery.parseJSON('%s'),\n" % json.dumps(pill))
    js_metrics.write("];\n")
    js_metrics.write("\n")

    print("Saving js_metrics file")
    js_metrics.write("periodChoices = [\n")
    for period_choice in config["period_choices"]:
        js_metrics.write('    {value: %(value)s, name: "%(name)s"},\n' % period_choice)
    js_metrics.write("];\n")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: %s <config.yaml> <from-AAAA-mm-dd> <to-AAAA-mm-dd> [extra-args]" % sys.argv[0],
              file=sys.stderr)
        sys.exit(1)
    try:
        main(sys.argv)
    finally:
        DBFactory.close_all()
    print("End")
