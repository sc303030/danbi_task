import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from task.models import SubTask, Task, Team

User = get_user_model()


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def teams(db):
    team_list = [Team(name=f"{i}") for i in ["DAN", "DA", "BEULL", "CHEOL", "TTAN", "HAE", "SU"]]
    Team.objects.bulk_create(team_list)


@pytest.fixture
def user(db, teams):
    team = Team.objects.get(name="DAN")
    user = User.objects.create_user(username="testuser", password="123456789", team=team)
    return user


@pytest.fixture
def user2(db, teams):
    team = Team.objects.get(name="DA")
    user = User.objects.create_user(username="testuser2", password="123456789", team=team)
    return user


@pytest.fixture
def user_client(db, user, api_client):
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def task_one(db, user_client):
    team = Team.objects.get(name="DAN")
    url = "/task/"
    payload = {
        "team": team.id,
        "title": "테스트 title",
        "content": "테스트 content",
        "add_sub_task": "블라블라,수피,단비",
    }
    response = user_client.post(url, payload)
    task = Task.objects.get(pk=response.json()["pk"])
    return task


@pytest.fixture
def task_two(db, teams, user_client):
    team = Team.objects.get(name="DAN")
    url = "/task/"
    payload = {
        "team": team.id,
        "title": "테스트 title",
        "content": "테스트 content",
        "add_sub_task": "단비",
    }
    response = user_client.post(url, payload)
    task = Task.objects.get(pk=response.json()["pk"])
    return task


@pytest.fixture
def task_three(db, teams, user_client):
    team = Team.objects.get(name="DAN")
    url = "/task/"
    payload = {
        "team": team.id,
        "title": "테스트 title",
        "content": "테스트 content",
        "add_sub_task": "단비,수피",
    }
    response = user_client.post(url, payload)
    task = Task.objects.get(pk=response.json()["pk"])
    sub_task = SubTask.objects.first()
    sub_task.is_complete = True
    sub_task.save()
    return task


@pytest.fixture
def task_four(db, teams, api_client, user2):
    api_client.force_authenticate(user2)
    team = Team.objects.get(name="DAN")
    url = "/task/"
    payload = {
        "team": team.id,
        "title": "테스트 title",
        "content": "테스트 content",
        "add_sub_task": "단비",
    }
    response = api_client.post(url, payload)
    task = Task.objects.get(pk=response.json()["pk"])
    return task
