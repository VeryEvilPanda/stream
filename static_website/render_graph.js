// Requires Google Charts, https://www.gstatic.com/charts/loader.js

function getGraph(graph_data, width, datatable, timeframe) {
    datatable.addColumn('datetime', 'Time');
    datatable.addColumn('number', 'Flow');
    for (var i = 0; i < graph_data.length; i++) {
        var date = graph_data[i][0]
        datatable.addRow([new Date(date[0], date[1], date[2], date[3], date[4]), graph_data[i][1]]);
    }
    if (timeframe == 'week') {
        var options = {
            title: 'Stream flow over the last week',
            titleTextStyle: {
                color: 'white',
                fontSize: 24,
                fontName: 'Glory',
                bold: true,
            },
            hAxis: {
                title: 'Time',
                format: 'MMM dd',
                titleTextStyle: {
                    color: 'white',
                    fontSize: 20,
                    fontName: 'Glory',
                    italic: false,
                },
                textStyle: {
                    color: 'white',
                    fontSize: 12,
                    fontName: 'Glory',
                },
                // gridlines: { 
                //     color: 'white',
                //     count: -1,
                //     units: {
                //         days: {format: ['MMM dd']},
                //     }
                // },
                minorGridlines: {
                    count: 0,
                }
            },
            vAxis: {
                title: 'Flow (m3/s)',
                titleTextStyle: {
                    color: 'white',
                    fontSize: 20,
                    fontName: 'Glory',
                    italic: false,
                },
                textStyle: {
                    color: 'white',
                    fontSize: 12,
                    fontName: 'Glory',
                },
                gridlines: { color: 'white' },
            },
            legend: 'none',
            backgroundColor: 'transparent',
            width: width,
            lineWidth: 4,
        };
    }
    else if (timeframe == 'day') {
        var options = {
            title: 'Stream flow over the last 24 hours',
            titleTextStyle: {
                color: 'white',
                fontSize: 24,
                fontName: 'Glory',
                bold: true,
            },
            hAxis: {
                title: 'Time',
                format: 'HH:mm',
                titleTextStyle: {
                    color: 'white',
                    fontSize: 20,
                    fontName: 'Glory',
                    italic: false,
                },
                textStyle: {
                    color: 'white',
                    fontSize: 12,
                    fontName: 'Glory',
                },
                // gridlines: { 
                //     color: 'white',
                //     count: -1,
                //     units: {
                //         days: {format: ['MMM dd']},
                //     }
                // },
                minorGridlines: {
                    count: 0,
                }
            },
            vAxis: {
                title: 'Flow (m3/s)',
                titleTextStyle: {
                    color: 'white',
                    fontSize: 20,
                    fontName: 'Glory',
                    italic: false,
                },
                textStyle: {
                    color: 'white',
                    fontSize: 12,
                    fontName: 'Glory',
                },
                gridlines: { color: 'white' },
            },
            legend: 'none',
            backgroundColor: 'transparent',
            width: width,
            lineWidth: 4,
        };
    }
    
    return [datatable, options];
}