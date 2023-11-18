import pytest
from rest_framework import status

from task.models import SubTask, Task


@pytest.mark.django_db(transaction=True)
def test_sub_task_complete(task_one, user, user_client):
    sub_task_id = task_one.tasks.get(team=user.team.id).id
    # When: complete sub task
    url = f"/sub-task/{sub_task_id}/complete/"
    response = user_client.patch(url)
    # Then: response.status_code equal 200 ok
    assert response.status_code == status.HTTP_200_OK
    # Then: sub_task.is_complete is True
    sub_task = SubTask.objects.get(pk=sub_task_id)
    assert sub_task.is_complete is True


@pytest.mark.django_db(transaction=True)
def test_auto_complete_task_after_all_sub_task_complete(task_two, user, user_client):
    # Given: Only one of the sub_task left is_complete is false
    sub_task_id = task_two.tasks.get(team=user.team.id).id
    # When: all sub_task complete after task auto complete

    url = f"/sub-task/{sub_task_id}/complete/"
    response = user_client.patch(url)
    # Then: task.is_complete is True
    task = Task.objects.get(pk=task_two.id)
    assert task.is_complete is True


@pytest.mark.django_db(transaction=True)
def test_fail_sub_task_complete(task_one, user, user_client, user2, api_client):
    api_client.force_authenticate(user2)
    sub_task_id = task_one.tasks.get(team=user.team.id).id
    # When: complete sub task
    url = f"/sub-task/{sub_task_id}/complete/"
    response = api_client.patch(url)
    # Then: response.status_code equal 403 forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN
