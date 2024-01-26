queue()
	.defer(d3.json, lineChartDataUrl)
    .await(ready);

function ready(error, dataset) {
    d3lineChart(dataset);
}