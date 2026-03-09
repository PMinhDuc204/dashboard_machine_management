from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys

from accounts.models import Machine_Logs

# Add scada_fx5u_li to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scada_fx5u_li'))
import plc_comm

@login_required(login_url="/authentication/login")
def home(request):
    max_id = Machine_Logs.objects.aggregate(max_id=Max('id'))['max_id']
    context = {
        'max_id': max_id
    }
    return render(request, "home.html", context)

@login_required(login_url="/authentication/login")
def machine_detail(request):
    return render(request, "machine_detail.html")

@login_required(login_url="/authentication/login")
def plc_control(request):
    return render(request, "plc_control.html")

def custom_404(request, exception):
    return render(request, 'page_404.html', status=404)

@csrf_exempt
def api_connect_plc(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ip = data.get('ip', '192.168.1.10')
            port = data.get('port', 5011)
            action = data.get('action', 'connect')
            
            if action == 'connect':
                success = plc_comm.connect_plc(ip, port)
                return JsonResponse({'status': 'ok' if success else 'failed', 'connected': plc_comm.connected})
            elif action == 'disconnect':
                plc_comm.connected = False
                # Optionally close socket if pymcprotocol supports it, but simple boolean toggle is fine
                return JsonResponse({'status': 'ok', 'connected': False})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'ok', 'connected': plc_comm.connected})

@csrf_exempt
def api_plc_status(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    try:
        data = plc_comm.read_words()
        if not data:
            data = {}
            
        # Also read some devices like D100, M80, M5000
        d100 = plc_comm.read_device('D100')
        m80 = plc_comm.read_device('M80')
        m5000 = plc_comm.read_device('M5000')
        
        # Read parameters from PLC: D500, D502, D300, D302, D304, D306
        d_params = plc_comm.read_device('D300', 20) # Read D300 to D319
        d_params2 = plc_comm.read_device('D500', 3) # Read D500 to D502
        
        status = {
            'status': 'ok',
            'data': data,
            'd100': d100[0] if d100 else 0,
            'm80': m80[0] if m80 else 0,
            'm5000': m5000[0] if m5000 else 0,
            'params': {
                'D300': d_params[0] if d_params else 0,
                'D302': d_params[2] if d_params else 0,
                'D304': d_params[4] if d_params else 0,
                'D306': d_params[6] if d_params else 0,
                'D500': d_params2[0] if d_params2 else 0,
                'D502': d_params2[2] if d_params2 else 0,
            }
        }
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def api_plc_command(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            command = data.get('command')
            if not command:
                return JsonResponse({'status': 'error', 'message': 'No command'})
            
            # command could be 'X100', 'M5001', 'X300'...
            success = plc_comm.write_device(command, [1])
            if success:
                # Typically, pulse signals like buttons need to turn off again unless the PLC handles rising edge
                # If these are X/M contacts intended as buttons (like UI buttons), we might NOT need to turn them off from here if self-latching
                # But let's assume setting to 1 is what the SCADA UI does.
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'failed'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'failed'})

@csrf_exempt
def api_plc_write_params(request):
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Example data: {"D500": 100, "D502": 200...}
            for key, val in data.items():
                if key.startswith('D'):
                    plc_comm.write_device(key, [int(val)])
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'failed'})
