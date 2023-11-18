from task.models import Task


def sub_task_save_handler(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields", None)
    if update_fields:
        obj = instance.task.tasks.all()
        is_all_complete = Task.is_all_complete_sub_task(obj)
        if is_all_complete:
            instance.task.complete()


def sub_task_delete_handler(sender, instance, **kwargs):
    obj = instance.task.tasks.all()
    is_all_complete = Task.is_all_complete_sub_task(obj)
    if is_all_complete:
        instance.task.complete()
