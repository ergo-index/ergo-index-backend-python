"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home)
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view())
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from backend.ergo_index_fund_api.views import views

urlpatterns = [
    # Auth endpoint.
    path('api/token/new', TokenObtainPairView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),

    # User endpoint.
    path('api/user/new/', views.new_user),
    path('api/user/profile/', views.user_profile),

    # Fund endpoint.
    path('api/fund/save/', views.save_fund),

    # Not-found endpoint.
    path('', views.do_nothing)
]
