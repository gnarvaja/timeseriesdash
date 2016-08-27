metrics = [
    new Metric("Inflación", "bar-chart", "inflacion", "yellow", "month"),
    new Metric("Inflación %", "bar-chart", "inflacion_h", "cyan", "month"),
    new Metric("Dólar x día", "bar-chart", "dolarxdia", "primary", "day"),
    new Metric("Dólar", "bar-chart", "dolar", "orange", "month"),
    new Metric("Inflación Acumulada", "bar-chart", "inflacion_accum", "orange", "month"),
    new Metric("Inflación Acumulada %", "bar-chart", "inflacion_accum_h", "cyan", "month"),
    new Metric("Soja Precio Internacional (u$s) x día", "bar-chart", "soja_int_xdia", "yellow", "day"),
    new Metric("Maíz Precio Internacional (u$s) x día", "bar-chart", "maiz_int_xdia", "orange", "day"),
    new Metric("Maíz Precio Internacional (u$s)", "bar-chart", "maiz_int", "primary", "month"),
    new Metric("Soja Precio Internacional (u$s)", "bar-chart", "soja_int", "primary", "month"),
    new Metric("Porcentaje Retención Soja", "bar-chart", "retencion_soja", "yellow", "month"),
    new Metric("Porcentaje Retención Maiz", "bar-chart", "retencion_maiz", "primary", "month"),
    new Metric("Soja Pesos Corrientes (en  puerto)", "bar-chart", "soja_pesos", "red", "month"),
    new Metric("Soja Pesos Constantes", "bar-chart", "soja_pesos_real", "orange", "month"),
    new Metric("Maíz Pesos Corrientes (en  puerto)", "bar-chart", "maiz_pesos", "yellow", "month"),
    new Metric("Maíz Pesos Constantes", "bar-chart", "maiz_pesos_real", "cyan", "month"),
];


pills = [
jQuery.parseJSON('{"active": true, "template": "templates/commodities.html", "commoditie_name": "soja", "key": "soja", "name": "Soja"}'),
jQuery.parseJSON('{"template": "templates/commodities.html", "commoditie_name": "maiz", "key": "maiz", "name": "Ma\u00edz"}'),
jQuery.parseJSON('{"name": "Inflaci\u00f3n / D\u00f3lar", "key": "datos_base", "template": "templates/datos_base.html"}'),
];

periodChoices = [
    {value: 1, name: "Mes"},
    {value: 2, name: "Bimestre"},
    {value: 3, name: "Trimestre"},
    {value: 4, name: "Cuatrimestre"},
    {value: 6, name: "Semestre"},
    {value: 12, name: "Año"},
];
