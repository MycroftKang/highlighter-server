from django.urls import include, path
from drf_yasg.utils import swagger_auto_schema
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from mgauth import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)


class TokenObtainPairView(jwt_views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshView(jwt_views.TokenRefreshView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


token_create_view = swagger_auto_schema(
    "POST", operation_summary="Create a user api token", security=[]
)(TokenObtainPairView.as_view())

token_refresh_view = swagger_auto_schema(
    "POST", operation_summary="Refresh a user api token", security=[]
)(TokenRefreshView.as_view())

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", token_create_view, name="token_obtain_pair"),
    path(
        "auth/token/refresh/",
        token_refresh_view,
        name="token_refresh",
    ),
]
