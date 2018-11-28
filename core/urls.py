# .. Imports
from rest_framework_nested import routers
from django.contrib import admin
from authentication.views import AccountViewSet, VerifiesViewSet
from django.conf.urls import url, include
from authentication.views import AccountViewSet, LoginView#, LogoutView
from authentication.views import LogoutView
from rest_framework_jwt.views import obtain_jwt_token
router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'verifies', VerifiesViewSet)
accounts_router = routers.NestedSimpleRouter(
    router, r'accounts', lookup='account'
)

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include(accounts_router.urls)),
    url(r'^api/v1/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api/v1/auth/token/$', obtain_jwt_token),
]
