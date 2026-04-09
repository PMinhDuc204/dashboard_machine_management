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
      var errPct = total > 0 ? Math.round((errors / total) * 100) : 0;
      var passPct = total > 0 ? Math.round((pass / total) * 100) : 0;
      document.getElementById('prog-errors').style.width = errPct + '%';
      document.getElementById('prog-pass').style.width = passPct + '%';
    })
    .catch(function(err) { console.warn('Stats API error:', err); });
}
updateProductStats();
setInterval(function() {
  updateProductStats();
}, 30000);

