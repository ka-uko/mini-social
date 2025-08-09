from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # задел на будущее (аватар, био и т.п.)
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # bio = models.TextField(blank=True)
    pass