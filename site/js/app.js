// vim set

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})


// Create a new module
var app = angular.module('radiocut_metrics',
    ['ui.bootstrap', 'chart.js', 'ui.slider', 'LocalStorageModule']);

app.filter("megaNumber", function() {
    return function(number, fractionSize) {

        if(number === null) return null;
        if(number === 0) return "0";

        if(!fractionSize || fractionSize < 0)
            fractionSize = 1;

        var abs = Math.abs(number);
        var rounder = Math.pow(10,fractionSize);
        var isNegative = number < 0;
        var key = '';
        var powers = [
            {key: "Q", value: Math.pow(10,15)},
            {key: "T", value: Math.pow(10,12)},
            {key: "B", value: Math.pow(10,9)},
            {key: "M", value: Math.pow(10,6)},
            {key: "K", value: 1000},
            {key: "", value: 1}
        ];

        for(var i = 0; i < powers.length; i++) {

            var reduced = abs / powers[i].value;

            reduced = Math.round(reduced * rounder) / rounder;

            if(reduced >= 1){
                abs = reduced;
                key = powers[i].key;
                break;
            }
        }

        return (isNegative ? '-' : '') + abs + key;
    };
});


app.controller("ComparativeMetricsCtrl", function ($scope, $http, localStorageService) {
  $scope.pills = pills;
  $scope.metrics = metrics;
  $scope.periodChoices = periodChoices;
  $scope.periods_back = localStorageService.get("periods_back") || 0;

  $scope.period_count = localStorageService.get("period_count") || 1;
  $scope.periods_text = $scope.period_count.toString();

  var disabled_metrics = localStorageService.get("disabled_metrics") || [];

  _.each($scope.metrics, function (metric, index) {
    $http.get(metric.get_data_url()).then(function (data) {
      $scope.metrics[index].data = data.data;
    });
    metric.bind_options($scope);
    if (_.contains(disabled_metrics, metric.key)) {
      metric.enabled = false;
    }
  });

  $scope.get_chart_labels = function (metric_names) {
    var varname = "chart_labels_" + metric_names.join("_");
    if (!angular.isDefined($scope[varname])) {
      $scope[varname] = $scope.getMetric(metric_names[0]).get_labels();
    }
    return $scope[varname];
  };
  $scope.get_chart_series = function (metric_names) {
    var varname = "chart_series_" + metric_names.join("_");
    if (!angular.isDefined($scope[varname])) {
      $scope[varname] = _.map(metric_names, function (metric_name) {
        return $scope.getMetric(metric_name).name;
      });
    }
    return $scope[varname];
  };
  $scope.get_chart_data = function (metric_names) {
    var varname = "chart_data_" + metric_names.join("_");
    if (!angular.isDefined($scope[varname])) {
      $scope[varname] =  _.map(metric_names, function (metric_name) {
        return _.map($scope.getMetric(metric_name).data, function (data_item) {
          return data_item.data;
        });
      });
    }
    return $scope[varname];
  };
  $scope.get_chart_colors = function (metric_names) {
    var varname = "chart_colors_" + metric_names.join("_");
    if (!angular.isDefined($scope[varname])) {
      $scope[varname] = _.map(metric_names, function (metric_name) {
        return $scope.getMetric(metric_name).color;
      });
    }
    return $scope[varname];
  };
  $scope.get_chart_dataset_override = function (yaxis) {
    var varname = angular.isDefined(yaxis) ? "chart_dataset_override_" + yaxis : "chart_dataset_override_undefined";
    if (!angular.isDefined($scope[varname])) {
      if (!angular.isDefined(yaxis))
        $scope[varname] = [];
      else
        $scope[varname] = _.map(yaxis, function (side) {
          if (side === "r")
            return {yAxisID: "y-axis-right"};
          else
            return {yAxisID: "y-axis-left"};
        });
    }
    return $scope[varname];
  };
  $scope.get_chart_options = function (yaxis) {
    var varname = angular.isDefined(yaxis) ? "chart_options_" + yaxis : "chart_options_undefined";
    if (!angular.isDefined($scope[varname])) {
      if (!angular.isDefined(yaxis))
        $scope[varname] = [];
      else {
        $scope[varname] = {
          scales: {
            yAxes: [
              {
                id: 'y-axis-left',
                type: 'linear',
                display: true,
                position: 'left'
              },
              {
                id: 'y-axis-right',
                type: 'linear',
                display: true,
                position: 'right'
              }
            ]
          }
        };
      }
    }
    return $scope[varname];
  };

  $scope.constants = constants;

  $scope.getMetric = function(metricKey) {
    return _.find($scope.metrics, function (m) { return m.key == metricKey; });
  };

  $scope.expand_metric_names = function (metric_names) {
    if (_.isArray(metric_names))
      return metric_names;
    var varname = "_expand_metric_names_" + metric_names;
    if (!angular.isDefined($scope[varname])) {
      var regexp = new RegExp(metric_names);
      $scope[varname] = _.pluck(_.filter($scope.metrics, function (m) { return m.key.match(regexp) !== null; }),
                                "key");
    }
    return $scope[varname];
  };

  $scope.save = function () {
    localStorageService.set("period_count", $scope.period_count);
    localStorageService.set("periods_back", $scope.periods_back);
    localStorageService.set("disabled_metrics", _.map(_.filter($scope.metrics, function (metric) { return !metric.enabled; }),
                                                              function (metric) { return metric.key }));
  };

  $scope.refresh = function () {
    $scope.period_count = parseInt($scope.periods_text);
  };

  $scope.refresh();
});

app.directive('thumbwidget', function() {
  return {
    restrict: 'E',
    scope: {
      precision: "=",
      isPercentage: "=",
      upDownPolicy: "@",
      badgePolicy: "@",
      metric: "="
    },
    templateUrl: 'widgets/thumb.html'
  };
});
