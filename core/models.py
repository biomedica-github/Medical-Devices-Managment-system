from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    cargo_ingeniero = "Ingeniero"
    cargo_jefe = "Jefe"
    cargo_admin = "Admin"
    cargo_choices = [
        (cargo_ingeniero, "Ingeniero"),
        (cargo_jefe, "Jefe"),
        (cargo_admin, "Administrador")
    ]
    email = models.EmailField(unique=True)
    cargo = models.CharField(choices=cargo_choices, max_length=9)

    def __str__(self) -> str:
        return f"{self.username}"

