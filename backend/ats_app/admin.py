from django.contrib import admin

from ats_app.models import Job, ProcessRun, StageResult


class StageResultInline(admin.TabularInline):
    model = StageResult
    readonly_fields = ['stage', 'status', 'rating', 'notes', 'created_at', 'updated_at']
    extra = 0


class ProcessRunInline(admin.TabularInline):
    model = ProcessRun
    readonly_fields = ['status', 'retry_count', 'created_at']
    extra = 0


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ProcessRunInline]


@admin.register(ProcessRun)
class ProcessRunAdmin(admin.ModelAdmin):
    list_display = ['job', 'status', 'retry_count', 'created_at']
    list_filter = ['status']
    inlines = [StageResultInline]


@admin.register(StageResult)
class StageResultAdmin(admin.ModelAdmin):
    list_display = ['process_run', 'stage', 'status', 'rating', 'created_at']
    list_filter = ['stage', 'status']
