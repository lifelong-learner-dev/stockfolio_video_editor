from celery import shared_task
import ffmpeg
from .models import TrimCommand, ConcatCommand, Video
import os
import subprocess
from django.core.files import File

@shared_task
def execute_trim_command(trim_command_id):
    try:
        # TrimCommand와 관련된 Video 객체를 조회합니다.
        cmd = TrimCommand.objects.get(id=trim_command_id)
        video = Video.objects.get(id=cmd.video_no)
        input_file = video.file.path
        output_file = f"output/trim_{cmd.id}.mp4"

        # 출력 파일의 디렉토리가 존재하지 않으면 생성합니다.
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        def seconds_to_hhmmss(seconds):
            """
            주어진 초를 "HH:MM:SS" 형식의 문자열로 변환합니다.

            :param seconds: 변환할 총 초 (정수 또는 실수)
            :return: "HH:MM:SS" 형식의 문자열
            """
            # 초 단위로 입력된 값을 정수로 변환하여 시간, 분, 초 계산
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)

            # "HH:MM:SS" 형식의 문자열로 포맷팅
            return f"{hours:02}:{minutes:02}:{secs:02}"
        start_time = seconds_to_hhmmss(cmd.start_time)
        end_time = seconds_to_hhmmss(cmd.end_time)
        # ffmpeg 명령어를 실행합니다.
        command = [
            'ffmpeg',
            '-i', input_file,
            '-ss', start_time,  
            '-t', end_time,
            '-c:v', 'libx264',  # 인코딩 방식 지정
            '-c:a', 'aac',      # 오디오 코덱 지정
            '-strict', 'experimental',
            output_file
        ]

        # subprocess로 ffmpeg 명령어 실행
        result = subprocess.run(command, capture_output=True, text=True)

        # 명령어 실행 결과 확인
        if result.returncode != 0:
            print(f"Error during trimming: {result.stderr}")
            return

        print(f"Trimmed video saved to: {output_file}")

        # 트림된 비디오를 새로운 Video 객체로 저장합니다.
        with open(output_file, 'rb') as f:
            new_video_file = File(f)
            new_video = Video.objects.create(file=new_video_file)

        print(f"Trimmed video saved as: {new_video.file.name}")

    except Exception as e:
        print(f"Unexpected error: {e}")

@shared_task
def execute_concat_command(concat_command_id):
    try:
        cmd = ConcatCommand.objects.get(id=concat_command_id)
        input_files = [video.file.path for video in cmd.videos.all()]
        output_file = f"uploads/concat_{cmd.id}.mp4"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 파일 목록 저장할 임시 파일 경로 생성
        file_list_path = f"uploads/filelist_{cmd.id}.txt"

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

        # 병합된 파일이 생성됐는지 확인
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
