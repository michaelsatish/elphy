$(document).ready(function() {
    const title = {text: null};
    const credits = {enabled: false};
    const tooltip = {enabled: false};
    
    // Render the Pie Chart
    Highcharts.chart("statusPieChart", {
        chart: {
            type: "pie"
        },
        title : title,
        credits: credits,
        tooltip: tooltip,
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: "pointer",
                dataLabels: {
                    enabled: true,
                    format: "<b>{point.name}</b>: {point.percentage:.1f} %",
                }
            }
        },
        series: [{
            name: 'Tests',
            colorByPoint: true,
            data: [
                {name: "Passed", y: totalPassed/totalTests, color: "#81c784"},
                {name: "Failed", y: totalFailed/totalTests, color: "#e57373"},
                {name: "Warning", y: totalWarning/totalTests, color: "#ffb74d"}
            ]
        }]
    });

    // Render the Column Chart
    Highcharts.chart("statusBarChart", {
        chart: {
            type: "column"
        },
        title : title,
        credits: credits,
        tooltip: tooltip,
        xAxis: {
            categories: ["Passed", "Failed", "Warning"]
        },
        yAxis: {
            min: 0,
            title: {
                text: null
            }
        },
        series: [
            {name: "Passed", data: [totalPassed], color: "#81c784"}, 
            {name: "Failed", data: [totalFailed], color: "#e57373"}, 
            {name: "Warning", data: [totalWarning], color: "#ffb74d"}
        ]
    });
});