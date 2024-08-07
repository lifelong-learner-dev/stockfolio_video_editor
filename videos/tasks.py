from celery import shared_task
import ffmpeg
from .models import TrimCommand, ConcatCommand, Video
import os

@shared_task
def execute_trim_command(trim_command_id):
    try:
        cmd = TrimCommand.objects.get(id=trim_command_id)
        input_file = cmd.video.file.path
        output_file = f"media/output/trim_{cmd.video.id}_{cmd.id}.mp4"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        (
            ffmpeg
            .input(input_file, ss=cmd.start_time / 1000, to=cmd.end_time / 1000)
            .output(output_file)
            .run()
        )
        cmd.video.file.name = output_file
        cmd.video.save()
    except Exception as e:
        print(f"Error trimming video: {e}")

@shared_task
def execute_concat_command(concat_command_id):
    try:
        cmd = ConcatCommand.objects.get(id=concat_command_id)
        input_files = [video.file.path for video in cmd.videos.all()]
        output_file = f"media/output/concat_{cmd.id}.mp4"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        (
            ffmpeg
            .input('concat:' + '|'.join(input_files))
            .output(output_file)
            .run()
        )
        new_video = Video.objects.create(file=output_file)
        TrimCommand.objects.filter(video__in=cmd.videos.all()).update(video=new_video)
        cmd.videos.clear()
        cmd.videos.add(new_video)
    except Exception as e:
        print(f"Error concatenating videos: {e}")