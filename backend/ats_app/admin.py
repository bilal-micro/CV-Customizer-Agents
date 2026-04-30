from django.contrib import admin
from ats_app.models import Job, ProcessRun, StageResult , UserProfile


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




# ==========================================
# الأسلوب الأول: تسجيل النموذج كجدول منفصل
# ==========================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # عرض الحقول في القائمة الخارجية
    list_display = ('user', 'preferred_model', 'has_api_key', 'created_at', 'updated_at')
    
    # إضافة خيارات البحث والفلترة
    search_fields = ('user__username', 'user__email', 'preferred_model')
    list_filter = ('preferred_model', 'created_at')
    
    # جعل حقول التواريخ للقراءة فقط لمنع التعديل اليدوي
    readonly_fields = ('created_at', 'updated_at')
    
    # استخدام autocomplete بدلاً من القائمة المنسدلة العادية (مفيد جداً عندما يكثر عدد المستخدمين)
    autocomplete_fields = ('user',) 

    # دالة مساعدة لعرض علامة صح/خطأ إذا كان مفتاح الـ API موجوداً (بدلاً من عرض المفتاح نفسه لأسباب أمنية)
    def has_api_key(self, obj):
        return bool(obj.openrouter_api_key)
    has_api_key.boolean = True
    has_api_key.short_description = 'Has API Key'


