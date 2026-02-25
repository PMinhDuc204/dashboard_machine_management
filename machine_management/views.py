from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from accounts.models import Machine_Logs

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

def custom_404(request, exception):
    return render(request, 'page_404.html', status=404)
