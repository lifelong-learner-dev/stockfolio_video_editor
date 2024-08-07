from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from .models import Video
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class VideoAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        # JWT 인증 설정
        self.client.login(username='testuser', password='testpassword')
        self.video_files = [
            SimpleUploadedFile('test1.mp4', b'file_content_1', content_type='video/mp4'),
            SimpleUploadedFile('test2.mp4', b'file_content_2', content_type='video/mp4'),
        ]

    def get_token_for_user(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token)

    def authenticate_client(self):
        # 사용자 토큰으로 클라이언트 인증
        token = self.get_token_for_user()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_video_upload_multiple(self):
        self.authenticate_client()
        response = self.client.post(reverse('video-list'), {'files': self.video_files}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), len(self.video_files))

    def test_trim_command(self):
        self.authenticate_client()
        upload_response = self.client.post(reverse('video-list'), {'files': self.video_files}, format='multipart')
        video_id = upload_response.data[0]['id']

        # 트림 명령 요청
        trim_data = {'video': video_id, 'start_time': 1000, 'end_time': 5000}
        response = self.client.post(reverse('video-detail', args=[video_id]), trim_data)
        if response.status_code != status.HTTP_201_CREATED:
            print("Trim Command Error:", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_download_video(self):
        self.authenticate_client()
        # 동영상 업로드
        upload_response = self.client.post(reverse('video-list'), {'files': self.video_files}, format='multipart')
        video_id = upload_response.data[0]['id']
        
        # 비디오 객체에서 파일 경로 확인
        video = Video.objects.get(id=video_id)
        file_path = video.file.path
        print(f"File path: {file_path}")

        # 경로가 존재하는지 확인
        self.assertTrue(os.path.exists(file_path), "File should exist")

        # 동영상 다운로드
        response = self.client.get(reverse('video-detail', args=[video_id]))

        # 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 응답의 Content-Type 확인
        self.assertEqual(response['Content-Type'], 'video/mp4')

        # 스트리밍된 콘텐츠를 가져와 파일의 크기와 비교
        downloaded_content = b''.join(response.streaming_content)
        original_file_size = os.path.getsize(file_path)
        downloaded_file_size = len(downloaded_content)
        self.assertEqual(downloaded_file_size, original_file_size, "Downloaded file size should match original file size")