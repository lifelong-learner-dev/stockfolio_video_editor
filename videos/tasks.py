from celery import shared_task
import ffmpeg
from .models import TrimCommand, ConcatCommand, Video
import os
import subprocess
from django.core.files import File

@shared_task
def execute_trim_command(trim_command_id):
    try:
        # TrimCommand 객체를 조회합니다.
        cmd = TrimCommand.objects.get(id=trim_command_id)
        
        # 원본 Video 객체를 조회합니다.
        video = Video.objects.get(id=cmd.video_no)
        
        # 원본 비디오 파일 경로와 출력 파일 경로를 설정합니다.
        input_file = video.file.path
        output_file = f"output/trim_{cmd.id}.mp4"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # ffmpeg를 사용하여 비디오를 트림합니다.
        (
            ffmpeg
            .input(input_file, ss=cmd.start_time / 1000, to=cmd.end_time / 1000)
            .output(output_file)
            .run()
        )
        
        # 트림된 비디오를 새 Video 객체로 저장합니다.
        with open(output_file, 'rb') as f:
            new_video_file = File(f)
            new_video = Video.objects.create(file=new_video_file)

        # 필요 시 추가 정보를 설정합니다. 예: 제목, 설명 등
        new_video.title = f"Trimmed Video {cmd.id}"
        new_video.save()

        print(f"Trimmed video saved as: {new_video.file.name}")

    except Exception as e:
        print(f"Error trimming video: {e}")

@shared_task
def execute_concat_command(concat_command_id):
    try:
        cmd = ConcatCommand.objects.get(id=concat_command_id)
        input_files = [video.file.path for video in cmd.videos.all()]
        output_file = f"media/uploads/concat_{cmd.id}.mp4"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 파일 목록을 저장할 임시 파일 경로 설정
        file_list_path = f"media/uploads/filelist_{cmd.id}.txt"

        # 파일 목록 생성
        with open(file_list_path, 'w') as filelist:
            for file_path in input_files:
                filelist.write(f"file '{file_path}'\n")

        # 파일 목록 내용 확인
        with open(file_list_path, 'r') as filelist:
            print("Contents of the file list:")
            print(filelist.read())

        # FFmpeg를 사용하여 파일 병합 실행
        try:
            subprocess.run(
                ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', file_list_path, '-c', 'copy', output_file],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")

        # 병합된 비디오 파일 확인
        if not os.path.exists(output_file):
            print(f"Output file not created: {output_file}")
            return

        # 임시 파일 목록 삭제
        os.remove(file_list_path)

        # 데이터베이스 업데이트
        new_video = Video.objects.create(file=output_file)
        cmd.videos.clear()
        cmd.videos.add(new_video)

    except Exception as e:
        print(f"Error concatenating videos: {e}")