from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    cargo_ingeniero = "Ingeniero"
    cargo_jefe = "Jefe"
    cargo_choices = [
        (cargo_ingeniero, "Ingeniero"),
        (cargo_jefe, "Jefe")
    ]

    email = models.EmailField(unique=True)
    cargo = models.CharField(choices=cargo_choices, max_length=9)