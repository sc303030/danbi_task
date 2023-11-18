from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from task.models import Team

User = get_user_model()


class Command(BaseCommand):
    help = "team 객체를 생성 하고 username=postman 객체를 한 개 생성합니다."

    def handle(self, *args, **options):
        danbi_team = Team.objects.get(name="DAN")
        dara_team = Team.objects.get(name="DA")
        danbi_user = User.objects.create_user(username="danbi", password="danbi", team=danbi_team)
        dara_user = User.objects.create_user(username="dara", password="dara", team=dara_team)
