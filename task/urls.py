from django.urls import include, path
from rest_framework import routers

from task.views import SubTaskViewSet, TaskViewSet

router = routers.DefaultRouter()
router.register("task", TaskViewSet)
router.register("sub-task", SubTaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
