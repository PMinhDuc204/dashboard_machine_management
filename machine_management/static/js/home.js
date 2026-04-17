$(document).ready(function() {
    "use strict";
    
    // Draw Weekly Chart (Area Spline style as requested)
    fetch('/api/stats/weekly/')
        .then(response => response.json())
        .then(res => {
            var weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
            
            // Create gradients if desired or just use solid colors like the reference
            new Chart(weeklyCtx, {
                type: 'line', // 'area-spline' equivalent in Chart.js
                data: {
                    labels: res.labels,
                    datasets: [
                        {
                            label: "Tổng (Total)",
                            backgroundColor: 'rgba(158, 158, 158, 0.5)', // gray #9e9e9e
                            borderColor: '#9e9e9e',
                            pointBackgroundColor: '#9e9e9e',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_total,
                        },
                        {
                            label: "Đạt (OK)",
                            backgroundColor: 'rgba(0, 150, 136, 0.5)', // teal #009688
                            borderColor: '#009688',
                            pointBackgroundColor: '#009688',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_pass,
                        },
                        {
                            label: "Lỗi (NG)",
                            backgroundColor: 'rgba(205, 220, 57, 0.5)', // lime #cddc39
                            borderColor: '#cddc39',
                            pointBackgroundColor: '#cddc39',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_fail,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        easing: 'easeInOutQuad',
                        duration: 520
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                fontColor: "rgba(0,0,0,0.5)",
                                fontStyle: "bold",
                            },
                            gridLines: {
                                color: 'rgba(200, 200, 200, 0.08)',
                                lineWidth: 1
                            }
                        }],
                        xAxes: [{
                            gridLines: {
                                color: 'rgba(200, 200, 200, 0.05)',
                                lineWidth: 1
                            },
                            ticks: {
                                fontColor: "rgba(0,0,0,0.5)",
                                fontStyle: "bold"
                            }
                        }]
                    },
                    tooltips: {
                        titleFontFamily: 'Open Sans',
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleFontColor: '#fff',
                        caretSize: 5,
                        cornerRadius: 4,
                        xPadding: 10,
                        yPadding: 10
                    }
                }
            });
        })
        .catch(err => console.error("Error fetching weekly stats:", err));

    // Draw Monthly Chart (Area Spline style)
    fetch('/api/stats/monthly/')
        .then(response => response.json())
        .then(res => {
            var monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
            
            new Chart(monthlyCtx, {
                type: 'line', // 'area-spline' equivalent in Chart.js
                data: {
                    labels: res.labels,
                    datasets: [
                        {
                            label: "Tổng (Total)",
                            backgroundColor: 'rgba(158, 192, 35, 0.5)', // yellow #9ec023
                            borderColor: '#9ec023',
                            pointBackgroundColor: '#788eb0ff',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_total,
                        },
                        {
                            label: "Đạt (OK)",
                            backgroundColor: 'rgba(31, 223, 14, 0.5)',
                            borderColor: '#1fdf0e',
                            pointBackgroundColor: '#0e1cdfff',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_pass,
                        },
                        {
                            label: "Lỗi (NG)",
                            backgroundColor: 'rgba(220, 57, 57, 0.5)',
                            borderColor: '#dc3939',
                            pointBackgroundColor: '#dc3939',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            data: res.data_fail,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        easing: 'easeInOutQuad',
                        duration: 520
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                fontColor: "rgba(0,0,0,0.5)",
                                fontStyle: "bold",
                            },
                            gridLines: {
                                color: 'rgba(200, 200, 200, 0.08)',
                                lineWidth: 1
                            }
                        }],
                        xAxes: [{
                            gridLines: {
                                color: 'rgba(200, 200, 200, 0.05)',
                                lineWidth: 1
                            },
                            ticks: {
                                fontColor: "rgba(0,0,0,0.5)",
                                fontStyle: "bold"
                            }
                        }]
                    },
                    tooltips: {
                        titleFontFamily: 'Open Sans',
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleFontColor: '#fff',
                        caretSize: 5,
                        cornerRadius: 4,
                        xPadding: 10,
                        yPadding: 10
                    }
                }
            });
        })
        .catch(err => console.error("Error fetching monthly stats:", err));

    // Real-time loop to poll PLC for Cycle time or other real-time stats
    setInterval(function() {
        $.get('/api/plc/status/', function(res) {
            if (res.status === 'ok') {
                $('#stat_cycle_time').text((res.d100 || 0) + ' ms'); // Just an example, maybe D100 is cycle time
            }
        });
    }, 2000);
});
