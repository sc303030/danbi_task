from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task"

    def ready(self):
        from task.models import SubTask
        from task.signals import sub_task_delete_handler, sub_task_save_handler

        post_save.connect(sub_task_save_handler, sender=SubTask)
        post_delete.connect(sub_task_delete_handler, sender=SubTask)
