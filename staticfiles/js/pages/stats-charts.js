var realtimeChart = null;
var realtimePassChart = null;

function updateProductStats() {
  fetch('/api/stats/products/')
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var total = data.total || 0;
      var errors = data.errors || 0;
      var pass = data.pass || 0;

      document.getElementById('stat-total').innerHTML = total + ' <small class="info">sản phẩm</small>';
      document.getElementById('stat-errors').innerHTML = errors + ' <small class="info">sản phẩm</small>';
      document.getElementById('stat-pass').innerHTML = pass + ' <small class="info">sản phẩm</small>';

      // Update progress bars
      var errPct = total > 0 ? Math.round((errors / total) * 100) : 0;
      var passPct = total > 0 ? Math.round((pass / total) * 100) : 0;
      document.getElementById('prog-errors').style.width = errPct + '%';
      document.getElementById('prog-pass').style.width = passPct + '%';
    })
    .catch(function(err) { console.warn('Stats API error:', err); });
}

function updateChart() {
  fetch('/api/stats/errors/?filter=realtime')
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var labels = data.trend.labels;
      var values = data.trend.data;

      if (realtimeChart) {
        realtimeChart.load({
          columns: [
            ['x'].concat(labels),
            ['Số SP lỗi'].concat(values)
          ]
        });
      } else {
        realtimeChart = c3.generate({
          bindto: '#chart-realtime-10h',
          data: {
            x: 'x',
            columns: [
              ['x'].concat(labels),
              ['Số SP lỗi'].concat(values)
            ],
            types: { 'Số SP lỗi': 'bar' },
            colors: { 'Số SP lỗi': '#FF5252' }
          },
          axis: {
            x: {
              type: 'category',
              tick: { rotate: -30, multiline: false }
            },
            y: {
              label: { text: 'Số SP lỗi', position: 'outer-middle' },
              min: 0
            }
          },
          bar: { width: { ratio: 0.6 } },
          grid: { y: { show: true } },
          tooltip: {
            format: {
              value: function(value) { return value + ' SP lỗi'; }
            }
          }
        });
      }

      var now = new Date();
      var hh = String(now.getHours()).padStart(2,'0');
      var mm = String(now.getMinutes()).padStart(2,'0');
      var ss = String(now.getSeconds()).padStart(2,'0');
      document.getElementById('chart-update-time').textContent = 'Cập nhật: ' + hh + ':' + mm + ':' + ss;
    })
    .catch(function(err) { console.warn('Chart API error:', err); });
}

function updatePassChart() {
  fetch('/api/stats/pass/')
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var labels = data.trend.labels;
      var values = data.trend.data;

      if (realtimePassChart) {
        realtimePassChart.load({
          columns: [
            ['x'].concat(labels),
            ['Số SP đạt'].concat(values)
          ]
        });
      } else {
        realtimePassChart = c3.generate({
          bindto: '#chart-realtime-pass-10h',
          data: {
            x: 'x',
            columns: [
              ['x'].concat(labels),
              ['Số SP đạt'].concat(values)
            ],
            types: { 'Số SP đạt': 'bar' },
            colors: { 'Số SP đạt': '#4CAF50' }
          },
          axis: {
            x: {
              type: 'category',
              tick: { rotate: -30, multiline: false }
            },
            y: {
              label: { text: 'Số SP đạt', position: 'outer-middle' },
              min: 0
            }
          },
          bar: { width: { ratio: 0.6 } },
          grid: { y: { show: true } },
          tooltip: {
            format: {
              value: function(value) { return value + ' SP đạt'; }
            }
          }
        });
      }

      var now = new Date();
      var hh = String(now.getHours()).padStart(2,'0');
      var mm = String(now.getMinutes()).padStart(2,'0');
      var ss = String(now.getSeconds()).padStart(2,'0');
      document.getElementById('chart-pass-update-time').textContent = 'Cập nhật: ' + hh + ':' + mm + ':' + ss;
    })
    .catch(function(err) { console.warn('Pass Chart API error:', err); });
}

// Manual refresh buttons
document.getElementById('btn-refresh-chart').addEventListener('click', function() {
  updateChart();
  updateProductStats();
});

document.getElementById('btn-refresh-pass-chart').addEventListener('click', function() {
  updatePassChart();
  updateProductStats();
});

// Initialize on load
updateProductStats();
updateChart();
updatePassChart();

// Auto-refresh every 30 seconds
setInterval(function() {
  updateProductStats();
  updateChart();
  updatePassChart();
}, 30000);
