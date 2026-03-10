from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(
        upload_to='profile_images',
        default='blank-profile-picture.png'
    )
    location = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username

class Machine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ErrorType(models.TextChoices):
    MISSING_COMPONENT = 'missing_component', 'Missing Component'
    MISPLACED_COMPONENT = 'misplaced_component', 'Misplaced Component'
    SOLDERING_DEFECT = 'soldering_defect', 'Soldering Defect'
    MISSING_PIN = 'missing_pin', 'Missing Pin'
    DEFECTIVE_LABEL = 'defective_label', 'Misaligned/Missing Label'
    WRONG_SHAPE_OR_POLARITY = 'wrong_shape_or_polarity', 'Wrong Shape/Polarity'

class Machine_Logs(models.Model):
    code_product = models.CharField(max_length=100)
    type_error = models.CharField(
        max_length=100,
        choices=ErrorType.choices,
        default=ErrorType.MISSING_COMPONENT
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.code_product

class Machine_Logs_Images(models.Model):
    image_url = models.ImageField(upload_to='machine_logs_images')
    machine_log = models.ForeignKey(Machine_Logs, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.machine_log.code_product
