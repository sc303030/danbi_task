import re

from django.contrib.auth import get_user_model
from rest_framework import serializers, status

from task.models import SubTask, Task, Team


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username"]


class SubTaskSerializer(serializers.ModelSerializer):
    team = serializers.ReadOnlyField(source="team.get_name_display")

    class Meta:
        model = SubTask
        fields = ["pk", "team", "is_complete"]
        read_only_fields = ("is_complete",)


class TaskSerializers(serializers.ModelSerializer):
    create_user = serializers.ReadOnlyField(source="create_user.username")
    add_sub_task = serializers.CharField(
        max_length=20,
        write_only=True,
        required=False,
        allow_null=True,
    )
    sub_task = SubTaskSerializer(source="tasks", many=True, read_only=True)

    def validate_add_sub_task(self, value):
        sub_task_list = re.findall(r"([가-힣]+),?", value)
        team_name = Team.get_team_name()
        for sub_task in sub_task_list:
            if sub_task not in team_name:
                raise serializers.ValidationError(
                    detail="팀을 찾을 수 없습니다.", code=status.HTTP_400_BAD_REQUEST
                )
        return value

    class Meta:
        model = Task
        fields = [
            "pk",
            "create_user",
            "team",
            "title",
            "content",
            "is_complete",
            "add_sub_task",
            "sub_task",
        ]
        read_only_fields = ("is_complete",)

    def create(self, validated_data):
        add_sub_task = validated_data.pop("add_sub_task", None)
        return super().create(validated_data)


class UpdateTaskSerializer(TaskSerializers, serializers.ModelSerializer):
    delete_sub_task = serializers.CharField(
        max_length=20,
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = TaskSerializers.Meta.fields + ["delete_sub_task"]
        read_only_fields = ("is_complete",)

    def create(self, validated_data):
        add_sub_task = validated_data.pop("add_sub_task", None)
        delete_sub_task = validated_data.pop("delete_sub_task", None)
        return super().create(validated_data)
