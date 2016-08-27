metrics = [
    new Metric("presupuesto_dunord", "bar-chart", "presupuesto_dunord", "green"),
    new Metric("presupuesto_km5", "bar-chart", "presupuesto_km5", "primary"),
    new Metric("presupuesto_mapuka", "bar-chart", "presupuesto_mapuka", "primary"),
    new Metric("Ventas KM5", "bar-chart", "sales_km5", "red"),
    new Metric("Ventas du Nord Store", "bar-chart", "sales_dunord", "brown"),
    new Metric("Ventas Mapuka", "bar-chart", "sales_mapuka", "orange"),
    new Metric("Ventas Totales", "bar-chart", "sales", "yellow"),
    new Metric("Presupuesto Total", "bar-chart", "presupuesto", "brown"),
    new Metric("Cumplimiento Presupuesto Iwana", "bar-chart", "ventas_vs_presupuesto_dunord", "primary"),
    new Metric("Cumplimiento Presupuesto KM5", "bar-chart", "ventas_vs_presupuesto_km5", "primary"),
    new Metric("Cumplimiento Presupuesto Mapuka", "bar-chart", "ventas_vs_presupuesto_mapuka", "green"),
    new Metric("Cumplimiento Presupuesto Total", "bar-chart", "ventas_vs_presupuesto", "red"),
];


pills = [
jQuery.parseJSON('{"active": true, "template": "templates/ventas_uninorte.html", "metric_suffix": "_km5", "key": "ventas_km5", "name": "Ventas KM5"}'),
jQuery.parseJSON('{"template": "templates/ventas_uninorte.html", "metric_suffix": "_dunord", "key": "ventas_dunord", "name": "Ventas DuNord"}'),
jQuery.parseJSON('{"template": "templates/ventas_uninorte.html", "metric_suffix": "_mapuka", "key": "ventas_mapuka", "name": "Ventas Mapuka"}'),
jQuery.parseJSON('{"template": "templates/ventas_uninorte.html", "metric_suffix": "", "key": "ventas_totales", "name": "Ventas Totales"}'),
jQuery.parseJSON('{"name": "Pedidos", "key": "pedidos", "template": "templates/pedidos_uninorte.html"}'),
];

periodChoices = [
    {value: 1, name: "Mes"},
    {value: 2, name: "Bimestre"},
    {value: 3, name: "Trimestre"},
    {value: 4, name: "Cuatrimestre"},
    {value: 6, name: "Semestre"},
    {value: 12, name: "Año"},
];
