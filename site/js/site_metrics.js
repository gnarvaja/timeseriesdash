metrics = [
    new Metric("Dólar", "bar-chart", "dolar", "brown", "month"),
    new Metric("Inflación", "bar-chart", "inflacion", "primary", "month"),
    new Metric("Inflación Acumulada", "bar-chart", "inflacion_accum", "green", "month"),
    new Metric("Soja Precio Internacional (u$s)", "bar-chart", "soja_int", "brown", "month"),
    new Metric("Porcentaje Retención Soja", "bar-chart", "retencion_soja", "primary", "month"),
    new Metric("Soja Pesos Corrientes", "bar-chart", "soja_pesos", "orange", "month"),
];


pills = [
jQuery.parseJSON('{"name": "Inflaci\u00f3n / D\u00f3lar", "key": "datos_base", "template": "templates/datos_base.html"}'),
jQuery.parseJSON('{"active": true, "template": "templates/commodities.html", "commoditie_name": "soja", "key": "soja", "name": "Ventas KM5"}'),
];

periodChoices = [
    {value: 1, name: "Mes"},
    {value: 2, name: "Bimestre"},
    {value: 3, name: "Trimestre"},
    {value: 4, name: "Cuatrimestre"},
    {value: 6, name: "Semestre"},
    {value: 12, name: "Año"},
];
