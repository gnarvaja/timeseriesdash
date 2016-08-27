constants = {
  chart_datasetOverride: [{ yAxisID: 'y-axis-left' }, { yAxisID: 'y-axis-right' }, { yAxisID: 'y-axis-left' }],
  chart_options: {
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
  },
};

moment.locale('es_AR');
