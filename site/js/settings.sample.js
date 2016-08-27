constants = {
  chart_datasetOverride: [{ yAxisID: 'y-axis-sales' }, { yAxisID: 'y-axis-sales' }, { yAxisID: 'y-axis-percent' }],
  chart_options: {
      scales: {
        yAxes: [
          {
            id: 'y-axis-sales',
            type: 'linear',
            display: true,
            position: 'left'
          },
          {
            id: 'y-axis-percent',
            type: 'linear',
            display: true,
            position: 'right'
          }
        ]
      }
  },
};

moment.locale('es_AR');
