from django.db import models

class Video(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='uploads/')
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.id}"

class TrimCommand(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    start_time = models.IntegerField()
    end_time = models.IntegerField()

class ConcatCommand(models.Model):
    videos = models.ManyToManyField(Video)