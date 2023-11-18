import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from task.models import SubTask, Task, Team

User = get_user_model()


def test_fail_authentication(db, api_client):
    # Given: Anonymous obj
    # When: Post task url not login
    url = "/task/"
    payload = {
        "team": "단비",
        "title": "task 테스트",
        "content": "DRF pytest 테스트 진행",
    }
    response = api_client.post(url, payload)
    # Then: response.status_code equal 403 forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_task_not_setting_team(db, user_client):
    # When: Post task url , payload not contain team
    url = "/task/"
    payload = {
        "title": "팀 없는 테스트",
        "content": "팀을 설정하지 않았습니다.",
    }
    response = user_client.post(url, payload)
    # Then: response.status_code equal status 400 bad request
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Then: response.json() filed txt equal ["이 필드는 필수 항목입니다."]
    assert response.json()["team"] == ["이 필드는 필수 항목입니다."]


@pytest.mark.parametrize(
    "name, title, content, expected",
    [
        ("DAN", "테스트1", "테스트1 content", status.HTTP_201_CREATED),
        ("SU", "테스트2", "테스트2 content", status.HTTP_201_CREATED),
        ("DA", "테스트3", "테스트3 content", status.HTTP_201_CREATED),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_create_task_empty_add_sub_task(user_client, name, title, content, expected):
    # Given: Team object id
    team = Team.objects.get(name=name)
    # When: Post task url , empty add_sub_task
    url = "/task/"
    payload = {
        "team": team.id,
        "title": title,
        "content": content,
    }
    response = user_client.post(url, payload)
    # Then: response.status_code equal expected
    assert response.status_code == expected
    # Then: task.objects.count() equal 1
    assert Task.objects.count() == 1


@pytest.mark.parametrize(
    "name, title, content, add_sub_task, expected_cnt, expected_code",
    [
        ("DAN", "테스트1", "테스트1 content", "단비,블라블라", 2, status.HTTP_201_CREATED),
        ("SU", "테스트2", "테스트2 content", "단비,블라블라,수피", 3, status.HTTP_201_CREATED),
        ("DA", "테스트3", "테스트3 content", "땅이,블라블라,수피,철로", 4, status.HTTP_201_CREATED),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_create_task_add_sub_task(
    user_client, name, title, content, add_sub_task, expected_cnt, expected_code
):
    # Given: Team object id
    team = Team.objects.get(name=name)
    # When: Post task url , payload contain add_sub_task
    url = "/task/"
    payload = {
        "team": team.id,
        "title": title,
        "content": content,
        "add_sub_task": add_sub_task,
    }
    response = user_client.post(url, payload)
    # Then: response.status_code equal expected_code
    assert response.status_code == expected_code
    # Then: task sub_task count equal expected_cnt
    task = Task.objects.first()
    assert task.tasks.count() == expected_cnt


@pytest.mark.parametrize(
    "name, title, content, add_sub_task, expected",
    [
        ("DAN", "테스트1", "테스트1 content", "단비,블라블라라", status.HTTP_400_BAD_REQUEST),
        ("SU", "테스트2", "테스트2 content", "단비비,블라블라,수피", status.HTTP_400_BAD_REQUEST),
        ("DA", "테스트3", "테스트3 content", "파이썬", status.HTTP_400_BAD_REQUEST),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_create_task_add_sub_task_wrong_team_name(
    user_client, name, title, content, add_sub_task, expected
):
    # Given: Team object id
    team = Team.objects.get(name=name)
    # When: Post task url add_sub_task contain wrong team_name
    url = "/task/"
    payload = {
        "team": team.id,
        "title": title,
        "content": content,
        "add_sub_task": add_sub_task,
    }
    response = user_client.post(url, payload)
    # Then: response.status_code equal expected
    assert response.status_code == expected
    # Then: response.json() filed txt equal ['팀을 찾을 수 없습니다.']
    assert response.json()["add_sub_task"] == ["팀을 찾을 수 없습니다."]


@pytest.mark.parametrize(
    "name, title, content, add_sub_task",
    [
        ("DAN", "테스트1", "테스트1 content", "블라블라"),
        ("SU", "테스트2", "테스트2 content", "단비"),
        ("DA", "테스트3", "테스트3 content", "철로"),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_create_task_add_sub_task_not_contain_owner_team(
    user_client, name, title, content, add_sub_task
):
    # Given: Team object id
    team = Team.objects.get(name=name)
    # When: Post task url
    url = "/task/"
    payload = {
        "team": team.id,
        "title": title,
        "content": content,
        "add_sub_task": add_sub_task,
    }
    response = user_client.post(url, payload)
    # Then: task.team.id not equal sub_task.team.id
    task = Task.objects.get(team=team.id)
    is_same_team = team.id == task.tasks.first().team.id
    assert is_same_team is False


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("title", "수정", "수정"),
        ("content", "수정", "수정"),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_patch_task_title_and_content(task_one, user_client, key, value, expected):
    # Given: task objects id
    # When: patch /task/id/
    url = f"/task/{task_one.id}/"
    payload = {key: value}
    response = user_client.patch(url, payload)
    result = Task.objects.filter(pk=task_one.pk).values_list(key, flat=True)[0]
    # Then: result equal expected
    assert result == expected


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("add_sub_task", "땅이", 4),
        ("delete_sub_task", "단비", 2),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_patch_task_sub_task(task_one, user_client, key, value, expected):
    # Given: task objects id
    # When: patch /task/id/
    url = f"/task/{task_one.id}/"
    payload = {key: value}
    response = user_client.patch(url, payload)
    task = Task.objects.get(pk=task_one.pk)
    # Then: task sub_task count equal expected
    assert task.tasks.count() == expected


@pytest.mark.django_db(transaction=True)
def test_patch_task_sub_task_add_delete(task_one, user_client):
    # Given: task objects id
    # When: patch /task/id/
    url = f"/task/{task_one.id}/"
    payload = {"add_sub_task": "땅이,해태", "delete_sub_task": "단비"}
    response = user_client.patch(url, payload)
    task = Task.objects.get(pk=task_one.pk)
    # Then: task sub_task count equal 4
    assert task.tasks.count() == 4


@pytest.mark.django_db(transaction=True)
def test_auto_complete_task_delete_sub_task(task_three, user_client):
    # Given: All is_complete is True except for the sub_task to be deleted
    # When: patch delete_sub_task
    url = f"/task/{task_three.pk}/"
    payload = {"delete_sub_task": "수피"}
    response = user_client.patch(url, payload)
    task = Task.objects.get(pk=task_three.pk)
    # Then: task.is_complete is True
    assert task.is_complete is True


@pytest.mark.parametrize(
    "value, expected",
    [
        ("수피,땅이", status.HTTP_404_NOT_FOUND),
        ("해태", status.HTTP_404_NOT_FOUND),
        ("철로,다래", status.HTTP_404_NOT_FOUND),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_patch_if_not_exist_team_in_sub_task(task_one, user_client, value, expected):
    # When: patch delete_sub_task
    url = f"/task/{task_one.pk}/"
    payload = {"delete_sub_task": value}
    response = user_client.patch(url, payload)
    # Then: response.status_code is expected
    assert response.status_code == expected


@pytest.mark.django_db(transaction=True)
def test_not_delete_is_complete_sub_task(task_three, user_client):
    # Given: sub_task has already been completed
    # When: patch delete_sub_task
    url = f"/task/{task_three.pk}/"
    payload = {"delete_sub_task": "단비"}
    response = user_client.patch(url, payload)
    # Then: task.tasks count equal 2
    task = Task.objects.get(pk=task_three.pk)
    assert task.tasks.count() == 2
    # Then: sub_task.is_complete is True
    sub_task = SubTask.objects.first()
    assert sub_task.is_complete is True
    # Then: sub_task.team.name is DAN
    assert sub_task.team.name == "DAN"


@pytest.mark.django_db(transaction=True)
def test_is_in_team_on_sub_task(api_client, user, task_four):
    # Given: sub_task in user team
    # When: get task
    api_client.force_authenticate(user)
    url = "/task/"
    response = api_client.get(url)
    result = response.json()
    # Then: result['create_user'] equal testuser2
    assert result[0]["create_user"] == "testuser2"
    # Then: result['sub_task'] is False
    assert result[0]["sub_task"][0]["is_complete"] is False


@pytest.mark.django_db(transaction=True)
def test_update_can_only_create_user(user_client, task_one):
    # When: task update
    url = f"/task/{task_one.pk}/"
    payload = {"title": "수정"}
    response = user_client.patch(url, payload)
    # Then: response.status_code equal 200 ok
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_fail_update_can_only_create_user(api_client, user2, task_one):
    # When: task update
    api_client.force_authenticate(user2)
    url = f"/task/{task_one.pk}/"
    payload = {"title": "수정"}
    response = api_client.patch(url, payload)
    # Then: response.status_code equal 400 forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN
