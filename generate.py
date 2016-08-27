#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import sys
import yaml
import plugins
import codecs
from utils import save_data
from utils.db import DBFactory


def main(argv):
    config_file = argv[1]

    ffrom = datetime.date(*map(int, argv[2].split("-")))
    tto = datetime.date(*map(int, argv[3].split("-")))

    config = yaml.load(open(config_file))

    js_metrics = codecs.open(config["js_metrics"], "wt", encoding="utf-8")

    js_metrics.write("metrics = [\n")

    for metric in config["metrics"]:
        metric_class = plugins.get_metric_class(metric["type"])
        if not metric_class:
            print >>sys.stderr, "Error no existe la métrica de tipo %s" % metric["type"]
            sys.exit(3)
        metric_obj = metric_class(config, metric, metric["name"])
        print "Generating metric %s" % metric["name"]
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

    print "Saving js_metrics file"
    js_metrics.write("periodChoices = [\n")
    for period_choice in config["period_choices"]:
        js_metrics.write('    {value: %(value)s, name: "%(name)s"},\n' % period_choice)
    js_metrics.write("];\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print >>sys.stderr, "Uso: %s <config.yaml> <from-AAAA-mm-dd> <to-AAAA-mm-dd>" % sys.argv[0]
        sys.exit(1)
    try:
        main(sys.argv)
    finally:
        DBFactory.close_all()
    print "End"