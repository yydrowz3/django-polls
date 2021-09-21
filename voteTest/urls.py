"""voteTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from polls import views
from django.conf import settings
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.show_index),
    path('api/subjects/', views.show_subjects),
    # path('api/subjects/', views.SubjectView.as_view()),
    path('api/teachers/', views.show_teachers),
    # path('api/teachers/', views.TeacherView.as_view()),
    path('praise/', views.praise_or_criticize),
    path('criticize/', views.praise_or_criticize),
    path('login/', views.login),
    path('register/', views.register),
    path('api/mobile/<str:tel>/', views.get_mobile_code),
    path('logout/', views.logout),
    path('captcha/', views.get_captcha),
    path('excel/', views.export_teachers_excel),
    path('teachers_data/', views.get_teachers_data),
    path('favicon.ico/', RedirectView.as_view(url='/static/images/favicon.ico')),
]

# router = DefaultRouter()
# router.register('api/subjects', views.SubjectViewSet)
# urlpatterns += router.urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.insert(0,  path('__debug__/', include(debug_toolbar.urls)))
