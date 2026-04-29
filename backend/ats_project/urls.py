from django.urls import include, path

# URL patterns - Include all routes from ats_app
urlpatterns = [
    path('api/', include('ats_app.urls')),
]
