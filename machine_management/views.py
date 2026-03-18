from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys

from accounts.models import Machine_Logs, ErrorType, ResultType
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMinute, TruncHour, TruncDay
from django.db.models import Count

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
        d_params = plc_comm.read_device('D300', 20)  # Read D300 to D319
        d_params2 = plc_comm.read_device('D500', 3)  # Read D500 to D502
        
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
            import time as _time
            data = json.loads(request.body)
            command = data.get('command')
            value = int(data.get('value', 1))
            readback = data.get('readback', False)
            if not command:
                return JsonResponse({'status': 'error', 'message': 'No command'})
            
            is_pulse = data.get('pulse', False)
            pulse_ms = int(data.get('pulse_ms', 200))

            if is_pulse:
                success, msg = plc_comm.pulse_device(command, pulse_ms)
            else:
                success, msg = plc_comm.write_device(command, [value])
            
            if not success:
                return JsonResponse({
                    'status': 'failed',
                    'command': command,
                    'write_value': value,
                    'message': msg if 'msg' in locals() else 'Write failed'
                })
            
            result = {
                'status': 'ok',
                'command': command,
                'write_value': value,
                'write_success': success,
            }
            
            # Đọc lại để xác nhận (read-back verification)
            if readback:
                _time.sleep(0.05)  # 50ms delay trước khi đọc lại
                try:
                    rb = plc_comm.read_device(command)
                    actual_value = rb[0] if rb else None
                    result['readback_value'] = actual_value
                    result['readback_match'] = (actual_value == value)
                    if actual_value != value:
                        result['readback_warning'] = (
                            f'Ghi {value} nhưng đọc lại được {actual_value} — '
                            f'PLC có thể không nhận lệnh hoặc X address không force được'
                        )
                except Exception as rb_err:
                    result['readback_error'] = str(rb_err)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'failed'})

@csrf_exempt
def api_plc_read_device(request):
    """Đọc trạng thái một địa chỉ PLC đơn lẻ (VD: X100, M80, D10...)"""
    if not plc_comm.connected:
        return JsonResponse({'status': 'failed', 'message': 'Not connected'})
    
    address = request.GET.get('address', '')
    if not address:
        return JsonResponse({'status': 'error', 'message': 'No address'})
    
    try:
        result = plc_comm.read_device(address)
        value = result[0] if result else 0
        return JsonResponse({'status': 'ok', 'address': address, 'value': value})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

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

@login_required(login_url="/authentication/login")
def api_error_stats(request):
    time_filter = request.GET.get('filter', 'realtime')
    now = timezone.now()
    
    data = []
    labels = []
    
    logs = Machine_Logs.objects.all()

    # For Distribution chart
    dist_logs = logs

    if time_filter == 'realtime':
        # Show last 10 hours, grouped by hour
        start_time = now - timedelta(hours=9)
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        logs = logs.filter(created__gte=start_time)
        dist_logs = logs
        grouped = logs.annotate(hour=TruncHour('created')).values('hour').annotate(count=Count('id')).order_by('hour')
        hour_map = {item['hour'].strftime('%H:00'): item['count'] for item in grouped}
        for i in range(9, -1, -1):
            h = now - timedelta(hours=i)
            h_str = h.strftime('%H:00')
            labels.append(h_str)
            data.append(hour_map.get(h_str, 0))

    elif time_filter == 'shift':
        today = now.date()
        shift1_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())).replace(hour=6)
        shift2_start = shift1_start.replace(hour=14)
        shift3_start = shift1_start.replace(hour=22)
        
        s1_count = logs.filter(created__gte=shift1_start, created__lt=shift2_start).count()
        s2_count = logs.filter(created__gte=shift2_start, created__lt=shift3_start).count()
        s3_count = logs.filter(created__gte=shift3_start).count() + logs.filter(created__lt=shift1_start, created__year=today.year, created__month=today.month, created__day=today.day).count()
        
        labels = ['Shift 1 (06-14)', 'Shift 2 (14-22)', 'Shift 3 (22-06)']
        data = [s1_count, s2_count, s3_count]
        
        dist_logs = logs.filter(created__year=today.year, created__month=today.month, created__day=today.day)

    elif time_filter == 'hour':
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        logs = logs.filter(created__gte=start_time)
        dist_logs = logs
        grouped = logs.annotate(hour=TruncHour('created')).values('hour').annotate(count=Count('id')).order_by('hour')
        hour_map = {item['hour'].hour: item['count'] for item in grouped}
        for i in range(24):
            labels.append(f"{i:02d}:00")
            data.append(hour_map.get(i, 0))

    elif time_filter == '10hour':
        start_time = now - timedelta(hours=9)
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
        
        logs = logs.filter(created__gte=start_time)
        dist_logs = logs
        grouped = logs.annotate(
            hour=TruncHour('created')
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        hour_map = {item['hour'].strftime('%H:00'): item['count'] for item in grouped}
        for i in range(9, -1, -1):
            h = now - timedelta(hours=i)
            h_str = h.strftime('%H:00')
            labels.append(h_str)
            data.append(hour_map.get(h_str, 0))

    elif time_filter == 'day':
        start_time = now - timedelta(days=6)
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        logs = logs.filter(created__gte=start_time)
        dist_logs = logs
        grouped = logs.annotate(day=TruncDay('created')).values('day').annotate(count=Count('id')).order_by('day')
        day_map = {item['day'].strftime('%Y-%m-%d'): item['count'] for item in grouped}
        for i in range(6, -1, -1):
            d = now - timedelta(days=i)
            d_str = d.strftime('%m-%d')
            labels.append(d_str)
            data.append(day_map.get(d_str, 0))
            
    # Chart 2: Error Distribution
    error_types = dist_logs.values('type_error').annotate(count=Count('id')).order_by('-count')
    error_choices = dict(ErrorType.choices)
    
    dist_labels = []
    dist_data = []
    for e in error_types:
        val = e['type_error']
        dist_labels.append(error_choices.get(val, val))
        dist_data.append(e['count'])

    return JsonResponse({
        'trend': {'labels': labels, 'data': data},
        'distribution': {'labels': dist_labels, 'data': dist_data}
    })

@login_required(login_url="/authentication/login")
def api_product_stats(request):
    """API trả về thống kê tổng SP, SP lỗi, SP đạt trong 10 giờ gần nhất."""
    now = timezone.now()
    start_time = now - timedelta(hours=10)

    # Tính toán thống kê tổng thể từ database
    total_pass = Machine_Logs.objects.filter(result=ResultType.PASS).count()
    total_errors = Machine_Logs.objects.filter(result=ResultType.FAIL).count()
    total_all = total_pass + total_errors

    # Trong 10h gần nhất
    errors_10h = Machine_Logs.objects.filter(created__gte=start_time, result=ResultType.FAIL).count()
    
    return JsonResponse({
        'total': total_all,
        'errors': total_errors,
        'pass': total_pass,
        'period_label': '10h gần nhất',
        'period_errors': errors_10h,
    })

@login_required(login_url="/authentication/login")
def api_pass_stats(request):
    """API trả về thống kê SP đạt theo 10 giờ gần nhất, phân bổ theo giờ."""
    now = timezone.now()
    start_time = now - timedelta(hours=9)
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    
    # Lấy tất cả logs PASS trong 10 giờ gần nhất
    pass_logs = Machine_Logs.objects.filter(
        created__gte=start_time,
        result=ResultType.PASS
    )
    
    # Nhóm theo giờ
    grouped = pass_logs.annotate(
        hour=TruncHour('created')
    ).values('hour').annotate(count=Count('id')).order_by('hour')
    
    hour_map = {item['hour'].strftime('%H:00'): item['count'] for item in grouped}
    
    labels = []
    data = []
    for i in range(9, -1, -1):
        h = now - timedelta(hours=i)
        h_str = h.strftime('%H:00')
        labels.append(h_str)
        data.append(hour_map.get(h_str, 0))
    
    return JsonResponse({
        'trend': {'labels': labels, 'data': data}
    })
