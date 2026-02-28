"""
Django management command: seed_data
======================================
Seed sample data for the machine_management project.

Usage:
    python manage.py seed_data                  # Default seeding
    python manage.py seed_data --flush           # Clear DB then seed
    python manage.py seed_data --users 5         # Custom user count
    python manage.py seed_data --machines 10     # Custom machines per user
    python manage.py seed_data --logs 20         # Custom logs per machine
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, Machine, Machine_Logs

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Minh", "Hung", "Lan", "Hoa", "Tuan", "Anh", "Long", "Phuc",
    "Dung", "Ngoc", "Thao", "Linh", "Khoa", "Binh", "Cuong",
]

LAST_NAMES = [
    "Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan",
    "Vu", "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly",
]

MACHINE_PREFIXES = [
    "CNC", "Robot", "Conveyor", "Press", "Lathe", "Mill",
    "Drill", "Grinder", "Welder", "Cutter", "Packager", "Sorter",
]

MACHINE_DESCRIPTIONS = [
    "High-precision metal machining center used in electronics component manufacturing line.",
    "Industrial robot automating assembly operations, integrated with AI vision sensors.",
    "Conveyor belt system for transporting products between production stages, variable speed.",
    "Metal sheet stamping machine, maximum pressing force 200 tons.",
    "5-axis CNC lathe for rotating part machining, accuracy +/-0.01mm.",
    "Vertical milling machine for high-precision flat surface and slot machining.",
    "Automatic drilling machine with CNC program, suitable for mass production lines.",
    "Surface grinder for metal surface treatment after rough machining.",
    "Automatic MIG/MAG welding machine with real-time weld quality inspection.",
    "CO2 laser cutting machine 500W, cuts thin metal sheets up to 6mm.",
    "Automatic packaging machine on production line, capacity 1200 products/hour.",
    "Product sorter by color and size using AI camera system.",
]

ERROR_TYPES = [
    "Overheating",
    "Sensor Malfunction",
    "Motor Failure",
    "Power Fluctuation",
    "Lubrication Failure",
    "Vibration Abnormal",
    "Communication Timeout",
    "Calibration Error",
    "Pressure Drop",
    "Spindle Jam",
    "Belt Slippage",
    "Emergency Stop Triggered",
    "Cooling System Failure",
    "PLC Error",
    "Encoder Fault",
]

PRODUCT_CODE_PREFIXES = ["SP", "LK", "MH", "MP", "CT", "KT"]

BIO_SAMPLES = [
    "Production line engineer with 5 years of experience in machine operation.",
    "Industrial machinery maintenance specialist, electrical and mechanical engineering.",
    "Production shift supervisor at mechanical machining workshop.",
    "CNC technician with Fanuc and Siemens certifications.",
    "Production supervisor responsible for product quality assurance.",
    "Industrial robot operator, specializing in ABB and KUKA systems.",
    "Automation engineer, PLC and SCADA programming.",
    "Machine data analyst and predictive maintenance specialist.",
]

LOCATIONS = [
    "Ha Noi", "Ho Chi Minh City", "Da Nang", "Binh Duong",
    "Dong Nai", "Hai Phong", "Can Tho", "Long An",
    "Vinh Phuc", "Bac Ninh", "Hung Yen", "Hai Duong",
]


def random_product_code() -> str:
    prefix = random.choice(PRODUCT_CODE_PREFIXES)
    number = random.randint(10000, 99999)
    suffix = random.choice(["A", "B", "C", "X", "Y", "Z"])
    return f"{prefix}-{number}-{suffix}"


# ---------------------------------------------------------------------------
# Management Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Seed sample data into database: Users, Profiles, Machines, Machine_Logs.\n"
        "Example: python manage.py seed_data --flush --users 5 --machines 8 --logs 15"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding (keeps superusers).",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=5,
            metavar="N",
            help="Number of regular users to create (default: 5).",
        )
        parser.add_argument(
            "--machines",
            type=int,
            default=6,
            metavar="N",
            help="Number of machines to create per user (default: 6).",
        )
        parser.add_argument(
            "--logs",
            type=int,
            default=10,
            metavar="N",
            help="Number of error logs to create per machine (default: 10).",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _print_section(self, title: str):
        width = 55
        self.stdout.write(self.style.HTTP_INFO("\n" + "-" * width))
        self.stdout.write(self.style.HTTP_INFO(f"  {title}"))
        self.stdout.write(self.style.HTTP_INFO("-" * width))

    def _flush_data(self):
        self._print_section("Flushing existing data ...")
        Machine_Logs.objects.all().delete()
        self.stdout.write("  [OK] Machine_Logs deleted")
        Machine.objects.all().delete()
        self.stdout.write("  [OK] Machines deleted")
        Profile.objects.all().delete()
        self.stdout.write("  [OK] Profiles deleted")
        deleted_count, _ = User.objects.filter(is_superuser=False).delete()
        self.stdout.write(
            f"  [OK] {deleted_count} regular Users deleted (superusers kept)"
        )

    def _create_admin(self):
        """Create superuser admin if not already present."""
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@machinemanagement.vn",
                password="Admin@123456",
                first_name="Admin",
                last_name="System",
            )
            Profile.objects.get_or_create(
                user=admin,
                defaults={
                    "bio": "System administrator for machine management platform.",
                    "location": "Ha Noi",
                },
            )
            self.stdout.write(
                self.style.SUCCESS("  [CREATED] Superuser: admin / Admin@123456")
            )
        else:
            self.stdout.write("  [SKIP] Superuser 'admin' already exists.")

    def _create_users(self, num_users: int):
        """Create regular users with Profiles."""
        users = []
        for i in range(1, num_users + 1):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            username = f"user_{i:02d}"
            email = f"{username}@factory.vn"

            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(f"  [SKIP] User '{username}' already exists.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="User@123456",
                    first_name=first,
                    last_name=last,
                    is_active=True,
                )
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "bio": random.choice(BIO_SAMPLES),
                        "location": random.choice(LOCATIONS),
                    },
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  [CREATED] User: {username} / User@123456")
                )
            users.append(user)
        return users

    def _create_machines(self, users, machines_per_user: int):
        """Create Machines for each user."""
        machines = []
        for user in users:
            used_names: set = set()
            for _ in range(machines_per_user):
                # Generate a unique machine name per user
                machine_name = None
                for _ in range(20):
                    prefix = random.choice(MACHINE_PREFIXES)
                    number = random.randint(100, 999)
                    candidate = f"{prefix}-{number}"
                    if candidate not in used_names:
                        machine_name = candidate
                        used_names.add(candidate)
                        break
                if machine_name is None:
                    machine_name = f"Machine-{random.randint(1000, 9999)}"

                machine = Machine.objects.create(
                    user=user,
                    name=machine_name,
                    description=random.choice(MACHINE_DESCRIPTIONS),
                )
                machines.append(machine)
        return machines

    def _create_machine_logs(self, machines, logs_per_machine: int):
        """Bulk-create Machine_Logs for every machine."""
        log_objects = []
        for machine in machines:
            for _ in range(logs_per_machine):
                log_objects.append(
                    Machine_Logs(
                        machine=machine,
                        code_product=random_product_code(),
                        type_error=random.choice(ERROR_TYPES),
                    )
                )

        Machine_Logs.objects.bulk_create(log_objects)
        return log_objects

    # ------------------------------------------------------------------
    # Main handler
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        num_users = options["users"]
        machines_per_user = options["machines"]
        logs_per_machine = options["logs"]
        do_flush = options["flush"]

        self.stdout.write(
            self.style.HTTP_INFO(
                "\n+==========================================+\n"
                "|   Machine Management -- Data Seeder     |\n"
                "+==========================================+"
            )
        )

        # 1. Flush (optional)
        if do_flush:
            self._flush_data()

        # 2. Superuser admin
        self._print_section("Creating Admin account")
        self._create_admin()

        # 3. Regular users
        self._print_section(f"Creating {num_users} regular Users")
        users = self._create_users(num_users)

        # 4. Machines
        total_machines = num_users * machines_per_user
        self._print_section(
            f"Creating Machines: {machines_per_user}/user x {num_users} users = {total_machines} total"
        )
        machines = self._create_machines(users, machines_per_user)
        self.stdout.write(
            self.style.SUCCESS(f"  [DONE] Created {len(machines)} machines")
        )

        # 5. Machine Logs
        total_logs = len(machines) * logs_per_machine
        self._print_section(
            f"Creating Logs: {logs_per_machine}/machine x {len(machines)} machines = {total_logs} total"
        )
        logs = self._create_machine_logs(machines, logs_per_machine)
        self.stdout.write(
            self.style.SUCCESS(f"  [DONE] Created {len(logs)} machine logs")
        )

        # 6. Summary
        self._print_section("Seeding complete!")
        self.stdout.write(
            self.style.SUCCESS(
                f"\n  Summary:\n"
                f"    Users (regular) : {User.objects.filter(is_superuser=False).count()}\n"
                f"    Superusers      : {User.objects.filter(is_superuser=True).count()}\n"
                f"    Profiles        : {Profile.objects.count()}\n"
                f"    Machines        : {Machine.objects.count()}\n"
                f"    Machine Logs    : {Machine_Logs.objects.count()}\n"
                f"\n  Default credentials:\n"
                f"    admin         / Admin@123456  (superuser)\n"
                f"    user_01 .. user_{num_users:02d} / User@123456\n"
            )
        )
