from django.conf import settings
from django.db import models
import re
from django.utils import timezone
from rest_framework.generics import get_object_or_404


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(TimestampedModel):
    class DepartmentChoices(models.TextChoices):
        DANBI = "DAN", "단비"
        DALAE = "DA", "다래"
        BEULLABEULLA = "BEULL", "블라블라"
        CHEOLLO = "CHEOL", "철로"
        TTANGI = "TTAN", "땅이"
        HAETAE = "HAE", "해태"
        SUPI = "SU", "수피"

    name = models.CharField(
        max_length=5,
        default=DepartmentChoices.DANBI,
        choices=DepartmentChoices.choices,
        db_index=True,
    )

    @classmethod
    def get_team_name(cls):
        return cls.DepartmentChoices.labels

    @classmethod
    def convert_team_name(cls, teams):
        teams = re.findall(r"([가-힣]+),?", teams)
        team_dict = {v: i for i, v in cls.DepartmentChoices.choices}
        teams = [team_dict[name] for name in teams]
        return teams

    def __str__(self):
        return f"{self.get_name_display()}"


class Task(TimestampedModel):
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_complete = models.BooleanField(default=False, db_index=True)
    completed_date = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        return f"task {self.title}"

    def is_user(self, user):
        return self.tasks.filter(team=user.team.id).exists()

    @staticmethod
    def is_all_complete_sub_task(obj):
        cnt = obj.count()
        complete_cnt = 0
        for sub_task in obj:
            if sub_task.is_complete:
                complete_cnt += 1
        if cnt == complete_cnt:
            return True
        return False

    def complete(self):
        self.is_complete = True
        self.completed_date = timezone.now()
        self.save(update_fields=["is_complete", "completed_date"])


class SubTask(TimestampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="tasks")
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False, db_index=True)
    completed_date = models.DateTimeField(null=True)

    def complete(self):
        self.is_complete = True
        self.completed_date = timezone.now()
        self.save(update_fields=["is_complete", "completed_date"])

    def __str__(self):
        return f"sub_task {self.task.id} {self.team.name}"

    @staticmethod
    def create_sub_task(sub_task_team, task):
        sub_tasks = []
        if sub_task_team:
            sub_task_team = Team.convert_team_name(sub_task_team)
            for name in sub_task_team:
                team = Team.objects.get(name=name)
                sub_task = SubTask(task=task, team=team)
                sub_tasks.append(sub_task)
            SubTask.objects.bulk_create(sub_tasks)

    @staticmethod
    def update_sub_task(delete_sub_task, add_sub_task, task):
        if delete_sub_task:
            delete_sub_task = Team.convert_team_name(delete_sub_task)
            for name in delete_sub_task:
                team = Team.objects.get(name=name)
                sub_task = get_object_or_404(SubTask, task=task, team=team)
                if not sub_task.is_complete:
                    sub_task.delete()
        if add_sub_task:
            add_sub_task = Team.convert_team_name(add_sub_task)
            for name in add_sub_task:
                team = Team.objects.get(name=name)
                sub_task, _ = SubTask.objects.get_or_create(task=task, team=team)
