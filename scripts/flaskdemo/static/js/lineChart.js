function d3lineChart(data) {
    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var arr = [];
    if (data.length >= 1) {
        arr = Object.keys(data[0]);
    }

    for (let i = 0; i < arr.length; ++i) {
        if(arr[i] === "_runtime" || arr[i] === "_timestamp") {
            continue;
        }

        // append the svg object to the body of the page

        var svg = d3.select("#lineChart")
          .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");

        var x = d3.scaleLinear()
          .domain([0, d3.max(data, function(d) { return d._runtime; }) + 5])
          .range([ 0, width ]);
        svg.append("g")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(x));
        // Add Y axis
        var y = d3.scaleLinear()
          .domain([d3.min(data, function(d) { return Reflect.get(d, arr[i]); }) - 2, d3.max(data, function(d) { return Reflect.get(d, arr[i]); }) + 2])
          .range([ height, 0 ]);
        svg.append("g")
          .call(d3.axisLeft(y));

        // Add X axis label:
        svg.append("text")
            .attr("text-anchor", "end")
            .attr("x", width)
            .attr("y", height + margin.top + 20)
            .text("Time(minutes)");

        // Y axis label:
        svg.append("text")
            .attr("text-anchor", "end")
            .attr("transform", "rotate(-90)")
            .attr("transform", "rotate(-90)")
            .attr("y", -margin.left + 20)
            .attr("x", -margin.top)
            .text(arr[i]);


        // Add the line
        svg.append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("stroke", "#69b3a2")
          .attr("stroke-width", 1.5)
          .attr("d", d3.line()
            .x(function(d) { return x(d._runtime) })
            .y(function(d) { return y(Reflect.get(d, arr[i])) })
            );

        // Add the points
        svg.append("g")
          .selectAll("dot")
          .data(data)
          .enter()
          .append("circle")
            .attr("cx", function(d) { return x(d._runtime) } )
            .attr("cy", function(d) { return y(Reflect.get(d, arr[i])) } )
            .attr("r", 5)
            .attr("fill", "#69b3a2");
    }

}