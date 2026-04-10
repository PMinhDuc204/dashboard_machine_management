$(function() {
    "use strict";
    initSparkline();
    initC3Chart();    
});

function initSparkline() {
    $(".sparkline").each(function() {
        var $this = $(this);
        $this.sparkline('html', $this.data());
    });
}
function initC3Chart() {
    setTimeout(function(){ 
        $(document).ready(function(){
            var chart = c3.generate({
                bindto: '#chart-area-spline-sracked',
                data: {
                    columns: [
                        ['data1', 21, 8, 32, 18, 19, 17, 23, 12, 25, 37],
                        ['data2', 7, 11, 5, 7, 9, 16, 15, 23, 14, 55],
                        ['data3', 13, 7, 9, 15, 9, 31, 8, 27, 42, 18],
                    ],
                    type: 'area-spline',
                    groups: [
                        [ 'data1', 'data2', 'data3']
                    ],
                    colors: {
                        'data1': Aero.colors["gray"],
                        'data2': Aero.colors["teal"],
                        'data3': Aero.colors["lime"],
                    },
                    names: {
                        'data1': 'Total Products',
                        'data2': 'Products Pass ',
                        'data3': 'Products Fail',
                    }
                },
                axis: {
                    x: {
                        type: 'category',
                        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'July', 'Aug', 'Sept', 'Oct']
                    },
                },
                legend: {
                    show: true,
                },
                padding: {
                    bottom: 0,
                    top: 0
                },
            });
        });    
        $(document).ready(function(){
            var chart = c3.generate({
                bindto: '#chart-pie',
                data: {
                    columns: [
                        ['data1', 55],
                        ['data2', 25],
                        ['data3', 20],
                    ],
                    type: 'pie',
                    colors: {
                        'data1': Aero.colors["lime"],
                        'data2': Aero.colors["teal"],
                        'data3': Aero.colors["gray"],
                    },
                    names: {
                        'data1': 'Arizona',
                        'data2': 'Florida',
                        'data3': 'Texas',
                    }
                },
                axis: {
                },
                legend: {
                    show: true,
                },
                padding: {
                    bottom: 0,
                    top: 0
                },
            });
        });

}, 500);
}
setTimeout(function(){
    "use strict";
    var mapData = {
        "US": 298,
        "SA": 200,
        "AU": 760,
        "IN": 2000000,
        "GB": 120,        
    };	
    if( $('#world-map-markers').length > 0 ){
        $('#world-map-markers').vectorMap({
            map: 'world_mill_en',
            backgroundColor: 'transparent',
            borderColor: '#fff',
            borderOpacity: 0.25,
            borderWidth: 0,
            color: '#e6e6e6',
            regionStyle : {
                initial : {
                fill : '#f4f4f4'
                }
            },

            markerStyle: {
            initial: {
                        r: 5,
                        'fill': '#fff',
                        'fill-opacity':1,
                        'stroke': '#000',
                        'stroke-width' : 1,
                        'stroke-opacity': 0.4
                    },
                },
        
            markers : [{
                latLng : [21.00, 78.00],
                name : 'INDIA : 350'
            
            },
            {
                latLng : [-33.00, 151.00],
                name : 'Australia : 250'
                
            },
            {
                latLng : [36.77, -119.41],
                name : 'USA : 250'
            
            },
            {
                latLng : [55.37, -3.41],
                name : 'UK   : 250'
            
            },
            {
                latLng : [25.20, 55.27],
                name : 'UAE : 250'
            
            }],

            series: {
                regions: [{
                    values: {
                        "US": '#49c5b6',
                        "SA": '#667add',
                        "AU": '#50d38a',
                        "IN": '#60bafd',
                        "GB": '#ff758e',
                    },
                    attribute: 'fill'
                }]
            },
            hoverOpacity: null,
            normalizeFunction: 'linear',
            zoomOnScroll: false,
            scaleColors: ['#000000', '#000000'],
            selectedColor: '#000000',
            selectedRegions: [],
            enableZoom: false,
            hoverColor: '#fff',
        });
    }
}, 800);