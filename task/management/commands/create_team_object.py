from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from task.models import Team

User = get_user_model()


class Command(BaseCommand):
    help = "team 객체를 생성 하고 username=postman 객체를 한 개 생성합니다."

    def handle(self, *args, **options):
        for name in ["DAN", "DA", "BEULL", "CHEOL", "TTAN", "HAE", "SU"]:
            obj, _ = Team.objects.get_or_create(name=name)

        danbi_team = Team.objects.get(name="DAN")
