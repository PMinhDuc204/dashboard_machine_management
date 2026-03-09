let isConnected = false;
let pollInterval = null;

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
            } else {
                clearInterval(pollInterval);
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
    if (isConnected) {
        dot.className = "badge badge-success";
        dot.innerText = "Đã kết nối PLC";
        note.innerText = "Sẵn sàng hoạt động...";
        document.getElementById('val_M80').innerText = "ĐANG TẢI...";
        document.getElementById('val_M80').className = "text-info font-weight-bold";
    } else {
        dot.className = "badge badge-danger";
        dot.innerText = "Chưa kết nối PLC";
        note.innerText = "Hệ thống đang chờ kết nối...";
        document.getElementById('val_M80').innerText = "OFF";
        document.getElementById('val_M80').className = "text-muted font-weight-bold";
    }
}

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
            
            // Don't overwrite input fields while user typing, only on first load or manual refresh 
            // Alternatively, only update inputs if they are not focused
            let activeElem = document.activeElement;
            if(data.params) {
                if(activeElem.id !== 'input_D500') $('#input_D500').val(data.params.D500);
                if(activeElem.id !== 'input_D502') $('#input_D502').val(data.params.D502);
                if(activeElem.id !== 'input_D300') $('#input_D300').val(data.params.D300);
                if(activeElem.id !== 'input_D302') $('#input_D302').val(data.params.D302);
                if(activeElem.id !== 'input_D304') $('#input_D304').val(data.params.D304);
                if(activeElem.id !== 'input_D306') $('#input_D306').val(data.params.D306);
            }
        } else if (data.status === 'failed') {
            isConnected = false;
            updateConnectUI();
            clearInterval(pollInterval);
        }
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
        body: JSON.stringify({command: address})
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            note.innerText = "Lệnh " + address + " đã thực thi thành công.";
        } else {
            note.innerText = "Lệnh " + address + " thất bại (" + data.message + ")";
        }
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
            alert("Lỗi cập nhật: " + resData.message);
        }
    });
}

function saveConfiguration() {
   alert("Đã lưu trạng thái hệ thống SCADA!"); 
}
