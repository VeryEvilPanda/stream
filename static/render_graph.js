// Requires Google Charts, https://www.gstatic.com/charts/loader.js


function drawGraph(graph_data) {
    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time');
    data.addColumn('number', 'Flow');
    for (var i = 0; i < graph_data.length; i++) {
        var date = graph_data[i][0]
        data.addRow([new Date(date[0], date[1], date[2], date[3], date[4]), graph_data[i][1]]);
    }
    var width = document.getElementById('main_body').clientWidth;
    var width = width * 0.9
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
            gridlines: { color: 'white' },
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

    var chart = new google.visualization.LineChart(document.getElementById('graph'));
    chart.draw(data, options);
    document.getElementById('graph').hidden = true;
}