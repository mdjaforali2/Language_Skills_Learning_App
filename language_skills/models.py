# language_skills/models.py

from django.db import models

class ListeningModule(models.Model):
    title = models.CharField(max_length=255)
    youtube_url = models.URLField(null=True)
    audio_file = models.FileField(upload_to='audio/', default='default_audio.mp3')
    captions = models.FileField(upload_to='text/', null=True, blank=True)

    def __str__(self):
        return self.title

# language_skills/models.py

from django.db import models

class ModuleQA(models.Model):
    module = models.ForeignKey(ListeningModule, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.TextField()

    FILL_IN_THE_GAPS = 'fill_in_the_gaps'
    MULTIPLE_CHOICE = 'multiple_choice'
    QUESTION_TYPES = [
        (FILL_IN_THE_GAPS, 'Fill in the Gaps'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=FILL_IN_THE_GAPS)
    choices = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.module.title} - {self.question}"

    def save(self, *args, **kwargs):
        # Your custom save logic goes here
        # For example, if you want to convert the answer to uppercase before saving

        # Call the parent class's save method
        super(ModuleQA, self).save(*args, **kwargs)


class UserAnswer(models.Model):
    module = models.ForeignKey(ListeningModule, on_delete=models.CASCADE)
    question = models.ForeignKey(ModuleQA, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.question.question}"

class SpeakingModule(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
