from django.shortcuts import render
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

def user_list(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'user_list.html', context)

def list_pcb(request):
    # Lấy logs từ 10 giờ gần nhất
    now = timezone.now()
    start_time = now - timedelta(hours=10)
    
    # Lấy tất cả logs từ 10 giờ gần nhất, sắp xếp theo thời gian mới nhất
    logs = Machine_Logs.objects.filter(created__gte=start_time).order_by('-created')[:400]
    
    # Calculate error type frequency for all logs in the last 10 hours
    error_counts = Machine_Logs.objects.filter(created__gte=start_time).values('type_error').annotate(count=Count('type_error')).order_by('-count')
    
    total_logs = Machine_Logs.objects.filter(created__gte=start_time).count()
    error_stats = []
    max_error = None
    
    for idx, e in enumerate(error_counts):
        enum_val = e['type_error']
        count = e['count']
        percentage = (count / total_logs * 100) if total_logs > 0 else 0
        
        # Get readable label from ErrorType choices
        label = dict(ErrorType.choices).get(enum_val, enum_val)
        
        stat = {
            'label': label,
            'count': count,
            'percentage': round(percentage, 2)
        }
        error_stats.append(stat)
        
        # The first item is the max error since we ordered by '-count'
        if idx == 0:
            max_error = stat
            
    context = {
        'logs': logs,
        'error_stats': error_stats,
        'max_error': max_error,
        'total_logs': total_logs,
        'machine_name': 'Last 10 Hours',
    }
    return render(request, 'list_pcb.html', context)