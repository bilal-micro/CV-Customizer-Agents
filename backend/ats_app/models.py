import uuid

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class UserProfile(models.Model):
    """User profile for storing OpenRouter API key and preferred model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    openrouter_api_key = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        default='',
        help_text="Your OpenRouter API key (required). Get it from https://openrouter.ai/keys"
    )
    preferred_model = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text="Your preferred OpenRouter model (required). Available models at https://openrouter.ai/models"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    latex_cv = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ProcessRun(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('awaiting_manual_input', 'Awaiting Manual Input'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='process_runs', null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='process_runs')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    iteration_count = models.PositiveIntegerField(default=0)
    max_iterations = models.PositiveIntegerField(default=5)
    manual_latex_input = models.TextField(blank=True)
    original_latex = models.TextField(blank=True)  # Store original latex for comparison
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ProcessRun {self.id} - {self.status}"


class StageResult(models.Model):
    STAGE_CHOICES = [
        ('keyword_extraction', 'Keyword Extraction'),
        ('cv_matching', 'CV Matching'),
        ('cv_update', 'CV Update'),
        ('ats_rating', 'ATS Rating'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process_run = models.ForeignKey(ProcessRun, on_delete=models.CASCADE, related_name='stage_results')
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(default=dict, blank=True)
    rating = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    iteration_notes = models.TextField(blank=True)
    manual_feedback = models.TextField(blank=True)
    iteration_number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ['process_run', 'stage']

    def __str__(self):
        return f"{self.stage} - {self.status}"
