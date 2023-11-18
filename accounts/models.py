from django.contrib.auth.models import AbstractUser
from django.db import models
from task.models import Task, Team


class User(AbstractUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
