import os
import sys
import django
import random
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'machine_management.settings')
django.setup()

from accounts.models import Machine_Logs, Machine

def seed():
    print("Clearing old Machine_Logs...")
    Machine_Logs.objects.all().delete()
    
    print("Seeding new Machine_Logs for the last 7 days...")
    
    # Fetch first machine if exists, else None
    machine = Machine.objects.first()
    
    now = timezone.now()
    logs_to_create = []

    # loop from 6 days ago up to today (total 7 days)
    for day_offset in range(6, -1, -1):
        target_day = now - timedelta(days=day_offset)
        
        # Create between 50 to 120 items per day
        num_logs = random.randint(50, 120)
        
        for _ in range(num_logs):
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            log_time = target_day.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
            
            # 80% pass, 20% fail
            status = 1 if random.random() < 0.8 else 0
            
            # Emulate some random label/switch fails if status=0
            label01_val = 1 if status == 1 else random.choice([0, 1])
            switch02_val = 1 if status == 1 else random.choice([0, 1])
            
            log = Machine_Logs(
                machine=machine,
                process_time_ms=round(random.uniform(55.0, 65.0), 2),
                caminput=1,
                grayfilter=1,
                shape01=1,
                pos01=1,
                label01=label01_val,
                switch01=1,
                shape02=1,
                pos02=1,
                switch02=switch02_val,
                resultdisplay=1,
                status=status
            )
            # Setting created field here does not work with bulk_create if auto_now_add is set,
            # but Machine_Logs 'created' uses default=timezone.now, so we can override it.
            log.created = log_time
            log.updated = log_time
            logs_to_create.append(log)
            
    Machine_Logs.objects.bulk_create(logs_to_create)
    print(f"Successfully seeded {len(logs_to_create)} logs across the last 7 days!")

if __name__ == '__main__':
    seed()
