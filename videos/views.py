import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
from .models import Video, TrimCommand, ConcatCommand
from .serializers import VideoSerializer, TrimCommandSerializer, ConcatCommandSerializer, VideoUploadSerializer
from .tasks import execute_trim_command, execute_concat_command
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os

# Logging setup
logger = logging.getLogger(__name__)


class VideoViewSet(viewsets.ViewSet):
    queryset = Video.objects.all()
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Ensure these parsers are set globally

    def list(self, request):
        queryset = Video.objects.all()
        serializer = VideoSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        manual_parameters=[
            openapi.Parameter(
                name='files',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_FILE),
                description='Video files to upload',
                required=True,
            ),
        ],
        responses={
            201: VideoSerializer(many=True),
            400: 'Bad Request',
        },
        consumes=['multipart/form-data'],
    )
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        logger.debug(f"Request files: {request.FILES}")
        serializer = VideoUploadSerializer(data=request.data)
        if serializer.is_valid():
            logger.debug("Serializer is valid")
            video_files = serializer.validated_data['files']
            created_videos = []
            for video_file in video_files:
                video = Video.objects.create(file=video_file)
                created_videos.append(VideoSerializer(video).data)
            return Response(created_videos, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        request_body=TrimCommandSerializer,
        responses={
            201: TrimCommandSerializer,
            400: 'Bad Request',
        }
    )
    @action(detail=True, methods=['post'], url_path='trim')
    def trim(self, request, pk=None):
        video = get_object_or_404(Video, pk=pk)
        serializer = TrimCommandSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                trim_command = serializer.save(video=video)
                transaction.on_commit(lambda: execute_trim_command.delay(trim_command.id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        request_body=ConcatCommandSerializer,
        responses={
            201: 'ID of the created concat command',
            400: 'Bad Request',
        }
    )
    @action(detail=False, methods=['post'], url_path='concat')
    def concat(self, request):
        # 'videos' 파라미터를 콤마로 분리하여 리스트로 변환
        video_ids = request.data.get('videos', '').split(',')
        
        try:
            # 비디오 ID에 해당하는 비디오 객체를 조회
            videos = Video.objects.filter(id__in=video_ids)
            if videos.count() != len(video_ids):
                return Response({'error': 'Some video IDs are invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # ConcatCommandSerializer에 비디오 객체 리스트를 전달하여 저장
            with transaction.atomic():
                concat_command = ConcatCommand.objects.create()
                concat_command.videos.set(videos)
                transaction.on_commit(lambda: execute_concat_command.delay(concat_command.id))
            
            return Response({'id': concat_command.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        responses={
            200: 'File download',
            404: 'File not found',
        }
    )
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        video = get_object_or_404(Video, pk=pk)
        if not video.file:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        file_path = video.file.path
        if not os.path.exists(file_path):
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type='video/mp4')
        response['Content-Length'] = os.path.getsize(file_path)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
