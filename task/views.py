from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from task.models import SubTask, Task
from task.permissions import IsCreateUserUpdateOrReadonly, IsTeamMemberUpdateOrReadonly
from task.serializers import SubTaskSerializer, TaskSerializers, UpdateTaskSerializer


class TaskViewSet(ModelViewSet):
    queryset = (
        Task.objects.all()
        .select_related("create_user")
        .select_related("team")
        .prefetch_related("tasks")
    )
    permission_classes = [IsAuthenticated, IsCreateUserUpdateOrReadonly]

    def get_serializer_class(self):
        if self.request.method in ["GET", "POST"]:
            return TaskSerializers
        return UpdateTaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "POST":
            qs = qs.filter(Q(team=self.request.user.team) | Q(tasks__team=self.request.user.team))
        return qs

    def perform_create(self, serializer):
        sub_task_team = self.request.data.get("add_sub_task", None)
        serializer.save(create_user=self.request.user, team=self.request.user.team)
        response = super().perform_create(serializer)
        SubTask.create_sub_task(sub_task_team, serializer.instance)
        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        add_sub_task = request.data.get("add_sub_task", None)
        delete_sub_task = request.data.get("delete_sub_task", None)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        SubTask.update_sub_task(delete_sub_task, add_sub_task, instance)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)


class SubTaskViewSet(ModelViewSet):
    queryset = SubTask.objects.all().prefetch_related("task")
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated, IsTeamMemberUpdateOrReadonly]

    @action(detail=True, methods=["PATCH"])
    def complete(self, request, pk):
        instance = self.get_object()
        instance.complete()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
