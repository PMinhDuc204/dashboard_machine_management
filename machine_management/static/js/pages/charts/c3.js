$(function() {
    "use strict";
    setTimeout(function(){ 
        $(document).ready(function(){
            fetch('/api/stats/weekly/')
                .then(response => response.json())
                .then(res => {
                    var chart = c3.generate({
                        bindto: '#chart-area-spline-sracked',
                        data: {
                            columns: [
                                ['data1'].concat(res.data_total),
                                ['data2'].concat(res.data_pass),
                                ['data3'].concat(res.data_fail)
                            ],
                            type: 'area-spline',
                            groups: [
                                [ 'data1', 'data2', 'data3']
                            ],
                            colors: {
                                'data1': Aero.colors["gray"] || '#9e9e9e',
                                'data2': Aero.colors["teal"] || '#009688',
                                'data3': Aero.colors["lime"] || '#cddc39'
                            },
                            names: {
                                'data1': 'Total Products',
                                'data2': 'Products Pass',
                                'data3': 'Products Fail'
                            }
                        },
                        axis: {
                            x: {
                                type: 'category',
                                categories: res.labels
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
                })
                .catch(err => console.error("Error fetching stats:", err));
        });

        $(document).ready(function(){
            fetch('/api/stats/monthly/')
                .then(response => response.json())
                .then(res => {
                    var chart = c3.generate({
                        bindto: '#chart-area-step',
                        data: {
                            columns: [
                                ['data1'].concat(res.data_total),
                                ['data2'].concat(res.data_pass),
                                ['data3'].concat(res.data_fail)
                            ],
                            type: 'area-spline',
                            groups: [
                                [ 'data1', 'data2', 'data3']
                            ],
                            colors: {
                                'data1': Aero.colors["yellow"] || '#9ec023ff',
                                'data2': Aero.colors["green"] || '#1fdf0eff',
                                'data3': Aero.colors["red"] || '#dc3939ff'
                            },
                            names: {
                                'data1': 'Total Products',
                                'data2': 'Products Pass',
                                'data3': 'Products Fail'
                            }
                        },
                        axis: {
                            x: {
                                type: 'category',
                                categories: res.labels
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
                })
                .catch(err => console.error("Error fetching stats:", err));
        });
    }, 500);
});