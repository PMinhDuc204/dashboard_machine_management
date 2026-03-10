import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Setup Django if this script is executed directly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "machine_management.settings")
django.setup()

from accounts.models import Machine, Machine_Logs, ErrorType

def run():
    machine = Machine.objects.first()
    if not machine:
        print("Không tìm thấy máy nào trong CSDL! Vui lòng chạy lệnh gieo dữ liệu trước.")
        return

    print(f"Đang thêm 100 bản ghi dữ liệu cho máy: {machine.name} (ID: {machine.id})")
    
    PRODUCT_CODE_PREFIXES = ["SP", "LK", "MH", "MP", "CT", "KT"]
    
    def random_product_code():
        prefix = random.choice(PRODUCT_CODE_PREFIXES)
        number = random.randint(10000, 99999)
        suffix = random.choice(["A", "B", "C", "X", "Y", "Z"])
        return f"{prefix}-{number}-{suffix}"
    
    logs = []
    error_choices = [
        ErrorType.MISSING_COMPONENT,
        ErrorType.MISPLACED_COMPONENT,
        ErrorType.SOLDERING_DEFECT,
        ErrorType.MISSING_PIN,
        ErrorType.DEFECTIVE_LABEL,
        ErrorType.WRONG_SHAPE_OR_POLARITY,
    ]
    
    for i in range(100):
        # Tạo thời gian ngẫu nhiên trong khoảng 30 ngày qua
        random_days = random.randint(0, 30)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        created_time = timezone.now() - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        log = Machine_Logs(
            machine=machine,
            code_product=random_product_code(),
            type_error=random.choice(error_choices)
        )
        # Chúng ta dùng created default khi save, nhưng vì đang dùng bulk_create nó sẽ bỏ qua auto_now_add, ta cần xét lại sau
        logs.append(log)
        
    Machine_Logs.objects.bulk_create(logs)
    print("Hoàn tất thêm 100 dòng dữ liệu mới!")

if __name__ == "__main__":
    run()
