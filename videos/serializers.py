from rest_framework import serializers
from .models import Video, TrimCommand, ConcatCommand

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class VideoUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )

class TrimCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrimCommand
        fields = ['video_no', 'start_time', 'end_time']

class ConcatCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcatCommand
        fields = '__all__'

class ConcatDetailSerializer(serializers.Serializer):
    video_nos = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    order_nos = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )