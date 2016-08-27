function Metric(name, icon, key, color, period_type) {
  var self = this;
  this.icon = icon;
  this.enabled = true;
  this.name = name;
  this.data = undefined;
  this.key = key;
  this.color = color;
  this.options = {
    period_count: 1,
    periods_back: 0
  };
  this.period_type = period_type;

  this.get_data_url = function () { return "data/" + self.key + ".json"; }

  this.is_loading = function () { return self.data === undefined; }

  this.bind_options = function (options) {
    self.options = options;
  }

  this.get_up_down_icon = function (policy) {
    policy = policy || "last_value";
    switch (policy) {
      case "last_value":
        if (self.get_current_value() > self.get_last_value()) {
          return "fa-thumbs-up";
        } else {
          return "fa-thumbs-down";
        }
        break;
      case "last_year":
        if (self.get_current_value() > self.get_last_year_value()) {
          return "fa-thumbs-up";
        } else {
          return "fa-thumbs-down";
        }
        break;
      case "percentage":
        if (self.get_current_value() >= 100.0) {
          return "fa-thumbs-up";
        } else {
          return "fa-thumbs-down";
        }
        break;
      case "positive":
        if (self.get_current_value() >= 0) {
          return "fa-thumbs-up";
        } else {
          return "fa-thumbs-down";
        }
        break;
    }
  };

  function sum_data(list) {
    return _.reduce(list, function(memo, obj) { return memo + obj.data; }, 0);
  }

  function _calc_index(position) {
    return position * self.options.period_count - self.options.periods_back
  }

  this.get_current_period = function() {
    if (!self.data) { return "1900-01-01"; }
    return self._format_label(self.data[self.data.length + _calc_index(-1)].label);
  }

  this.get_current_value = function() {
    if (!self.data) { return 1; }
    if (self.options.periods_back != 0) {
      return sum_data(self.data.slice(_calc_index(-1), -self.options.periods_back));
    } else {
      return sum_data(self.data.slice(_calc_index(-1)));
    }
  };

  this.get_last_value = function() {
    if (!self.data) { return 0; }
    return sum_data(self.data.slice(_calc_index(-2), _calc_index(-1)));
  };

  this.get_last_year_value = function() {
    if (!self.data) { return 0; }
    return sum_data(self.data.slice(_calc_index(-13), _calc_index(-12)));
  };

  this.get_grow_percent = function (policy) {
    var percent;
    policy = policy || "last_value";
    switch (policy) {
      case "last_value":
        percent = self.get_current_value() / self.get_last_value() - 1.0;
        break;
      case "last_year":
        percent = self.get_current_value() / self.get_last_year_value() - 1.0;
        break;
    }
    return percent * 100;
  };

  this.get_value = function () {
    return self.get_current_value();
  };

  this._format_label = function (label) {
    if (self.period_type == "month") {
        return moment(label).format("MMM YYYY");
    } else {
      return label;
    }
  };

  this.get_labels = function () {
    return _.map(self.data, function (data_item) { return self._format_label(data_item.label) } );
  };
};

