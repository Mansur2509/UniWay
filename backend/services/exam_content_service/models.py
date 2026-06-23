from django.db import models


class Exam(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False, db_index=True)

    def __str__(self) -> str:
        return self.name


class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("exam", "slug"), name="unique_exam_section_slug")
        ]


class Question(models.Model):
    class Origin(models.TextChoices):
        ORIGINAL = "original", "Original EduVerse content"
        LICENSED = "licensed", "Licensed content"

    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE, related_name="questions")
    prompt = models.TextField()
    origin = models.CharField(max_length=20, choices=Origin.choices, default=Origin.ORIGINAL)
    provenance_note = models.CharField(max_length=240, default="Original EduVerse demonstration content")
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer_choices")
    label = models.CharField(max_length=5)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Explanation(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="explanation")
    text = models.TextField()

