from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings


# URL patterns - Include all routes from ats_app
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ats_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
