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
        fields = '__all__'

class ConcatCommandSerializer(serializers.ModelSerializer):
    videos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Video.objects.all()
    )

    class Meta:
        model = ConcatCommand
        fields = ['videos']