let isConnected = false;
let pollInterval = null;

// ======= X100: Sườn xuống (Falling Edge / LDF) =======
// X100 trong ladder dùng ký hiệu ↓↑ = LDF (Load Falling Edge)
// PLC kích hoạt khi X100 chuyển 1→0 (sườn xuống)
// Luồng điều khiển từ web:
//   Nhấn nút → Force X100=1 → 200ms → Force X100=0 ← sườn xuống này kích hoạt PLC
const deviceState = {
    'X100': 0,
    'X100_pulsing': false,
};

function toggleConnect() {
    const action = isConnected ? 'disconnect' : 'connect';
    fetch('/api/plc/connect/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: action, ip: '192.168.1.10', port: 5011})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            isConnected = data.connected;
            updateConnectUI();
            if (isConnected) {
                pollInterval = setInterval(pollPlcStatus, 1000);
                // Đọc trạng thái X100 ngay lập tức khi kết nối
                readX100State();
            } else {
                clearInterval(pollInterval);
                resetX100UI();
            }
        } else {
            alert("Lỗi kết nối: " + data.message);
        }
    })
    .catch(err => alert("Lỗi hệ thống: " + err));
}

function updateConnectUI() {
    const dot = document.getElementById('plc_connection_dot');
    const note = document.getElementById('status_note');
    const connectBtn = document.querySelector('[onclick="toggleConnect()"]');
    if (isConnected) {
        dot.className = "badge badge-success";
        dot.innerText = "Đã kết nối PLC";
        note.innerText = "Sẵn sàng hoạt động...";
        document.getElementById('val_M80').innerText = "ĐANG TẢI...";
        document.getElementById('val_M80').className = "text-info font-weight-bold";
        if (connectBtn) {
            connectBtn.className = "btn btn-outline-danger btn-sm";
            connectBtn.innerText = "NGẮT KẾT NỐI";
        }
    } else {
        dot.className = "badge badge-danger";
        dot.innerText = "Chưa kết nối PLC";
        note.innerText = "Hệ thống đang chờ kết nối...";
        document.getElementById('val_M80').innerText = "OFF";
        document.getElementById('val_M80').className = "text-muted font-weight-bold";
        if (connectBtn) {
            connectBtn.className = "btn btn-outline-info btn-sm";
            connectBtn.innerText = "KẾT NỐI PLC";
        }
    }
}

// ======= Đọc trạng thái X100 từ PLC (phản hồi từ PLC sau khi thực hiện Origin) =======
function readX100State() {
    if (!isConnected) return;
    fetch('/api/plc/read_device/?address=X100')
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            deviceState['X100'] = data.value;
            // Chỉ cập nhật LED nếu không đang trong trạng thái pulse animation
            if (!deviceState['X100_pulsing']) {
                updateX100LED(data.value);
            }
        }
    })
    .catch(() => {});
}

// ======= Cập nhật LED trạng thái X100 (phản hồi PLC) =======
function updateX100LED(value) {
    const led = document.getElementById('led-x100');
    const ledInline = document.getElementById('led-x100-inline');
    const statusText = document.getElementById('x100-status-text');

    if (value === 1) {
        if (led) led.className = "led-indicator led-on";
        if (statusText) { statusText.innerText = "ĐANG THỰC HIỆN"; statusText.className = "font-weight-bold text-warning"; }
        if (ledInline) { ledInline.style.background = "#ffeb3b"; ledInline.style.boxShadow = "0 0 6px 3px #ffeb3baa"; }
    } else {
        if (led) led.className = "led-indicator led-idle";
        if (statusText) { statusText.innerText = "SẴN SÀNG"; statusText.className = "font-weight-bold text-info"; }
        if (ledInline) { ledInline.style.background = "#42a5f5"; ledInline.style.boxShadow = "0 0 4px 2px #42a5f555"; }
    }
}

function resetX100UI() {
    deviceState['X100'] = 0;
    deviceState['X100_pulsing'] = false;
    const led = document.getElementById('led-x100');
    const ledInline = document.getElementById('led-x100-inline');
    const statusText = document.getElementById('x100-status-text');
    const btn = document.getElementById('btn-x100-toggle');
    if (led) led.className = "led-indicator led-off";
    if (statusText) { statusText.innerText = "CHƯA KẾT NỐI"; statusText.className = "font-weight-bold text-muted"; }
    if (ledInline) { ledInline.style.background = "#9e9e9e"; ledInline.style.boxShadow = "none"; }
    if (btn) {
        btn.disabled = false;
        btn.className = "btn btn-primary btn-lg btn-block waves-effect mt-2";
        btn.innerHTML = '<i class="zmdi zmdi-home"></i> THỰC HIỆN ORIGIN (X100)';
    }
}

// ======= DEBUG LOGGER =======
const plcDebugLogs = [];
function debugLog(level, msg, data) {
    const now = new Date();
    const ts = now.toTimeString().slice(0,8) + '.' + String(now.getMilliseconds()).padStart(3,'0');
    const entry = { ts, level, msg, data };
    plcDebugLogs.unshift(entry);  // Mới nhất lên đầu
    if (plcDebugLogs.length > 50) plcDebugLogs.pop();
    renderDebugPanel();
    console.log(`[PLC ${level}] ${ts} ${msg}`, data || '');
}

function renderDebugPanel() {
    const panel = document.getElementById('plc-debug-log');
    if (!panel) return;
    panel.innerHTML = plcDebugLogs.slice(0, 20).map(e => {
        const icons = { OK: '✅', ERR: '❌', WARN: '⚠️', INFO: 'ℹ️', READBACK: '🔍' };
        const colors = { OK: '#00e676', ERR: '#ef5350', WARN: '#ff9800', INFO: '#42a5f5', READBACK: '#ce93d8' };
        const icon = icons[e.level] || '•';
        const color = colors[e.level] || '#ccc';
        let detail = '';
        if (e.data) {
            detail = '<span style="color:#aaa;font-size:0.85em;"> → ' +
                JSON.stringify(e.data).replace(/</g,'&lt;') + '</span>';
        }
        return `<div style="border-bottom:1px solid #333;padding:3px 0;">
            <span style="color:#888;font-size:0.8em;">${e.ts}</span>
            <span style="color:${color};margin:0 4px;">${icon}</span>
            <span style="color:#eee;">${e.msg}</span>${detail}
        </div>`;
    }).join('');
}

function clearDebugLog() {
    plcDebugLogs.length = 0;
    renderDebugPanel();
}

// ======= Lệnh ORIGIN — Ghi trực tiếp M200 (Internal Coil) =======
// M200 là internal coil → ghi được qua MC Protocol
// Chỉ cần SET M200=1 → PLC kích hoạt Origin sequence
// Không cần pulse 2 bước như X100 (physical input)
function triggerOriginX100() {
    if (!isConnected) {
        alert("Vui lòng kết nối PLC trước khi thực hiện Origin!");
        return;
    }
    if (deviceState['X100_pulsing']) return;

    const note = document.getElementById('status_note');
    const btn = document.getElementById('btn-x100-toggle');
    const led = document.getElementById('led-x100');
    const ledInline = document.getElementById('led-x100-inline');
    const statusText = document.getElementById('x100-status-text');

    deviceState['X100_pulsing'] = true;
    debugLog('INFO', 'Bắt đầu lệnh Origin → SET M200=1 (internal coil)');

    // UI: đang gửi
    if (btn) { btn.disabled = true; btn.className = "btn btn-warning btn-lg btn-block waves-effect mt-2"; btn.innerHTML = '<i class="zmdi zmdi-rotate-right zmdi-hc-spin"></i> ĐANG GỬI M200=1...'; }
    if (led) led.className = "led-indicator led-pulse-origin";
    if (statusText) { statusText.innerText = "Đang SET M200=1..."; statusText.className = "font-weight-bold text-warning"; }
    if (ledInline) { ledInline.style.background = "#ff9800"; ledInline.style.boxShadow = "0 0 8px 3px #ff9800aa"; }
    note.innerText = "[1/2] SET M200=1 + đọc lại...";

    // === Bước 1: Ghi M200=1 + readback ===
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: 'M200', value: 1, readback: true})
    })
    .then(res => res.json())
    .then(data => {
        debugLog(data.status === 'ok' ? 'OK' : 'ERR',
            `write_device(M200, 1) → status=${data.status}`, data);

        if (data.readback_value !== undefined) {
            const match = data.readback_match;
            debugLog('READBACK',
                `Đọc lại M200 = ${data.readback_value} | Khớp: ${match ? 'CÓ ✅' : 'KHÔNG ❌'}`,
                { write: 1, readback: data.readback_value, match }
            );
            if (!match) {
                debugLog('WARN', `⚠ Ghi M200=1 nhưng đọc lại = ${data.readback_value} — PLC không nhận!`);
                note.innerText = `⚠ CẢNH BÁO: Ghi M200=1 nhưng đọc lại = ${data.readback_value}`;
            }
        }

        if (data.status === 'ok' && data.readback_match !== false) {
            // Ghi thành công + readback khớp → xác nhận ngay
            note.innerText = "[2/2] M200=1 ✔ — Đọc lại để xác nhận...";
            if (statusText) { statusText.innerText = "⏳ Đang xác nhận M200..."; statusText.className = "font-weight-bold text-info"; }
            debugLog('OK', 'M200=1 đã ghi thành công, readback khớp');

            // Dù readback đã OK, đọc lại sau 300ms để chắc ăn (PLC scan cycle)
            setTimeout(() => {
                fetch('/api/plc/read_device/?address=M200')
                .then(res => res.json())
                .then(rb => {
                    const val = rb.value;
                    debugLog('READBACK',
                        `[Confirm] Đọc M200 sau 300ms = ${val} | Trạng thái: ${val === 1 ? 'ON ✅' : 'OFF ❌'}`,
                        { M200: val }
                    );

                    deviceState['X100_pulsing'] = false;
                    if (btn) { btn.disabled = false; btn.className = "btn btn-primary btn-lg btn-block waves-effect mt-2"; btn.innerHTML = '<i class="zmdi zmdi-home"></i> THỰC HIỆN ORIGIN (M200)'; }

                    if (val === 1) {
                        note.innerText = "✅ XÁC NHẬN: M200 = ON → Origin đang thực hiện!";
                        debugLog('OK', '✅ CONFIRMED: M200=ON — Origin đang chạy thực tế!');
                        if (led) led.className = "led-indicator led-done";
                        if (statusText) { statusText.innerText = "✅ M200=ON (Origin OK)"; statusText.className = "font-weight-bold text-success"; }
                        if (ledInline) { ledInline.style.background = "#00e676"; ledInline.style.boxShadow = "0 0 8px 4px #00e676cc"; }
                    } else {
                        note.innerText = "❌ M200 vẫn OFF sau khi ghi! Kiểm tra quyền ghi hoặc interlock.";
                        debugLog('ERR', '❌ FAILED: M200=OFF sau khi ghi — PLC từ chối hoặc có interlock');
                        if (led) led.className = "led-indicator led-off";
                        if (statusText) { statusText.innerText = "❌ M200=OFF (Thất bại)"; statusText.className = "font-weight-bold text-danger"; }
                        if (ledInline) { ledInline.style.background = "#ef5350"; ledInline.style.boxShadow = "none"; }
                    }

                    setTimeout(() => {
                        if (!deviceState['X100_pulsing']) {
                            if (led) led.className = "led-indicator led-idle";
                            if (statusText) { statusText.innerText = "SẴN SÀNG"; statusText.className = "font-weight-bold text-info"; }
                            if (ledInline) { ledInline.style.background = "#42a5f5"; ledInline.style.boxShadow = "0 0 4px 2px #42a5f555"; }
                        }
                    }, 4000);
                })
                .catch(err => {
                    debugLog('ERR', 'Lỗi đọc lại M200', { error: String(err) });
                    deviceState['X100_pulsing'] = false;
                    note.innerText = "⚠ Đã ghi M200=1 nhưng không đọc lại được. Quan sát máy thực tế.";
                    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="zmdi zmdi-home"></i> THỰC HIỆN ORIGIN (M200)'; btn.className = "btn btn-primary btn-lg btn-block waves-effect mt-2"; }
                    if (led) led.className = "led-indicator led-idle";
                    if (statusText) { statusText.innerText = "⚠ Không xác nhận được"; statusText.className = "font-weight-bold text-warning"; }
                });
            }, 300);

        } else {
            // Ghi thất bại hoặc readback không khớp
            deviceState['X100_pulsing'] = false;
            const errMsg = data.readback_match === false
                ? `❌ Ghi M200=1 nhưng readback=${data.readback_value} — PLC từ chối lệnh`
                : `❌ Lỗi ghi M200: ${data.message || 'Thất bại'}`;
            note.innerText = errMsg;
            debugLog('ERR', errMsg, data);
            if (btn) { btn.disabled = false; btn.className = "btn btn-primary btn-lg btn-block waves-effect mt-2"; btn.innerHTML = '<i class="zmdi zmdi-home"></i> THỰC HIỆN ORIGIN (M200)'; }
            if (led) led.className = "led-indicator led-off";
            if (statusText) { statusText.innerText = "❌ LỖI GHI M200"; statusText.className = "font-weight-bold text-danger"; }
            if (ledInline) { ledInline.style.background = "#ef5350"; ledInline.style.boxShadow = "none"; }
        }
    })
    .catch(err => {
        debugLog('ERR', 'Lỗi network khi ghi M200', { error: String(err) });
        deviceState['X100_pulsing'] = false;
        note.innerText = "❌ Lỗi kết nối: " + err;
        if (btn) { btn.disabled = false; btn.className = "btn btn-primary btn-lg btn-block waves-effect mt-2"; btn.innerHTML = '<i class="zmdi zmdi-home"></i> THỰC HIỆN ORIGIN (M200)'; }
        if (led) led.className = "led-indicator led-off";
        if (statusText) { statusText.innerText = "❌ LỖI MẠNG"; statusText.className = "font-weight-bold text-danger"; }
    });
}
// Alias
var toggleX100 = triggerOriginX100;

function pollPlcStatus() {
    if (!isConnected) return;
    fetch('/api/plc/status/')
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            if(data.data) {
                $('#val_cycle_time').text(data.data.cycle !== undefined ? data.data.cycle : 0);
                $('#val_D10').text(data.data.in !== undefined ? data.data.in : 0);
                $('#val_D14').text(data.data.ok !== undefined ? data.data.ok : 0);
                $('#val_D16').text(data.data.ng !== undefined ? data.data.ng : 0);
                $('#val_D12').text(data.data.out !== undefined ? data.data.out : 0);
                $('#val_D20').text(data.data.rate !== undefined ? data.data.rate : 0);
            }
            
            $('#val_D100').text(data.d100 !== undefined ? data.d100 : 0);
            
            if(data.m80 !== undefined) {
                if(data.m80 == 1) {
                    $('#val_M80').text('ON (Ready)');
                    $('#val_M80').removeClass().addClass('text-success font-weight-bold');
                } else {
                    $('#val_M80').text('OFF');
                    $('#val_M80').removeClass().addClass('text-muted font-weight-bold');
                }
            }
            
            if(data.m5000 !== undefined) {
                if(data.m5000 == 1) {
                    $('#val_M5000').text('ON (Alarm)');
                    $('#val_M5000').removeClass().addClass('text-danger font-weight-bold');
                } else {
                    $('#val_M5000').text('OFF');
                    $('#val_M5000').removeClass().addClass('text-muted font-weight-bold');
                }
            }
            
            let activeElem = document.activeElement;
            if(data.params) {
                if(activeElem.id !== 'input_D500') $('#input_D500').val(data.params.D500);
                if(activeElem.id !== 'input_D502') $('#input_D502').val(data.params.D502);
                if(activeElem.id !== 'input_D300') $('#input_D300').val(data.params.D300);
                if(activeElem.id !== 'input_D302') $('#input_D302').val(data.params.D302);
                if(activeElem.id !== 'input_D304') $('#input_D304').val(data.params.D304);
                if(activeElem.id !== 'input_D306') $('#input_D306').val(data.params.D306);
            }

            // Cập nhật trạng thái X100 mỗi 5 lần poll (mỗi 5 giây)
            if (typeof pollX100Counter === 'undefined') window.pollX100Counter = 0;
            window.pollX100Counter++;
            if (window.pollX100Counter % 5 === 0) {
                readX100State();
            }

        } else if (data.status === 'failed') {
            isConnected = false;
            updateConnectUI();
            clearInterval(pollInterval);
            resetX100UI();
        }
    })
    .catch(err => {
        // Lỗi network khi poll — không alert để tránh spam
        console.warn('[PLC Poll] Lỗi kết nối:', err);
    });
}

function sendPlcCommand(address) {
    if(!isConnected) {
        alert("Vui lòng kết nối PLC trước khi gửi lệnh!");
        return;
    }
    const note = document.getElementById('status_note');
    note.innerText = "Đang gửi lệnh tới: " + address + " ...";
    
    fetch('/api/plc/command/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: address, value: 1})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = "Lệnh " + address + " đã thực thi thành công.";
        } else {
            note.innerText = "Lệnh " + address + " thất bại (" + (data.message || 'không rõ lý do') + ")";
        }
    })
    .catch(err => {
        console.warn('[PLC Command] Lỗi:', err);
        note.innerText = "⚠ Lỗi gửi lệnh " + address + ": " + err;
    });
}

function saveParameters() {
    if(!isConnected) {
        alert("Vui lòng kết nối PLC trước khi cập nhật tham số!");
        return;
    }
    const data = {
        D500: document.getElementById('input_D500').value,
        D502: document.getElementById('input_D502').value,
        D300: document.getElementById('input_D300').value,
        D302: document.getElementById('input_D302').value,
        D304: document.getElementById('input_D304').value,
        D306: document.getElementById('input_D306').value,
    };
    
    document.getElementById('status_note').innerText = "Đang cập nhật tham số...";
    
    fetch('/api/plc/write_params/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(resData => {
        if (resData.status === 'ok') {
            document.getElementById('status_note').innerText = "Đã cập nhật tham số cài đặt thành công.";
        } else {
            document.getElementById('status_note').innerText = "⚠ Lỗi cập nhật: " + (resData.message || 'Thất bại');
        }
    })
    .catch(err => {
        console.warn('[PLC Params] Lỗi:', err);
        document.getElementById('status_note').innerText = "⚠ Lỗi kết nối khi lưu tham số: " + err;
    });
}

function saveConfiguration() {
   alert("Đã lưu trạng thái hệ thống SCADA!"); 
}

// ======= Global error handler =======
// Bắt tất cả unhandled promise rejection để tránh lỗi "Uncaught (in promise)"
window.addEventListener('unhandledrejection', function(event) {
    // Bỏ qua lỗi từ extension của browser (onboarding.js, v.v.)
    if (event.reason && event.reason.stack &&
        (event.reason.stack.includes('onboarding') ||
         event.reason.stack.includes('extension'))) {
        return;
    }
    console.warn('[PLC] Unhandled Promise Rejection:', event.reason);
    event.preventDefault(); // Ngăn lỗi hiện ra console như "Uncaught"
});
