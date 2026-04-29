from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ats_app.views import JobViewSet, ProcessRunViewSet, StageResultViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'process-runs', ProcessRunViewSet)
router.register(r'stage-results', StageResultViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('ats_app.urls')),
]
