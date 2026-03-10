from django.shortcuts import render
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages

def user_list(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'user_list.html', context)

from django.db.models import Count

def list_pcb(request):
    # Lấy máy đầu tiên có trong database
    machine = Machine.objects.first()
    
    if not machine:
        return render(request, 'list_pcb.html', {'logs': [], 'error_stats': [], 'total_logs': 0, 'machine_name': 'Unknown'})
        
    logs = Machine_Logs.objects.filter(machine=machine).order_by('-created')
    
    # Calculate error type frequency
    error_counts = logs.values('type_error').annotate(count=Count('type_error')).order_by('-count')
    
    total_logs = logs.count()
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
        'machine_name': machine.name,
    }
    return render(request, 'list_pcb.html', context)