from django.urls import path
from .views import VideoViewSet

video_list = VideoViewSet.as_view({
    'get': 'list',
    'post': 'upload'
})

video_detail = VideoViewSet.as_view({
    'post': 'trim',
    'get': 'download'
})

concat_videos = VideoViewSet.as_view({
    'post': 'concat'
})

urlpatterns = [
    path('', video_list, name='video-list'),
    path('<int:pk>/', video_detail, name='video-detail'),
    path('concat/', concat_videos, name='video-concat'),
]
