from engagements.models import Job
from engagements.serializers.work_item_serializers import (
    WorkItemSerializer,
    WorkItemListSerializer,
    WorkItemCreateSerializer,
    WorkItemUpdateSerializer,
)


class JobListSerializer(WorkItemListSerializer):
    class Meta(WorkItemListSerializer.Meta):
        model = Job
        fields = WorkItemListSerializer.Meta.fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]
        read_only_fields = WorkItemListSerializer.Meta.read_only_fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]


class JobSerializer(WorkItemSerializer):
    class Meta(WorkItemSerializer.Meta):
        model = Job
        fields = WorkItemSerializer.Meta.fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]


class JobCreateSerializer(WorkItemCreateSerializer):
    class Meta(WorkItemCreateSerializer.Meta):
        model = Job
        fields = WorkItemCreateSerializer.Meta.fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]
        read_only_fields = WorkItemCreateSerializer.Meta.read_only_fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]


class JobUpdateSerializer(WorkItemUpdateSerializer):
    class Meta(WorkItemUpdateSerializer.Meta):
        model = Job
        fields = WorkItemUpdateSerializer.Meta.fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]
        read_only_fields = WorkItemUpdateSerializer.Meta.read_only_fields + [
            "job_code",
            "assigned_team",
            "estimated_hours",
        ]
