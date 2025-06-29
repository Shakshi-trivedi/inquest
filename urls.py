"""
URL configuration for inquest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from backoffice_engine import views
from inquest import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index),
    path('login/',views.login),
    path('register/',views.register),
    path('about/',views.about),
    path('profile/',views.profile),
    path('team/',views.team),
    path('success/',views.success),
    path('pricing/',views.pricing),
    path('forgot-password/',views.sendotp),
    path('reset-password/',views.reset),
    path('services/',views.service),
    path('dashboard/',views.dashboard),
    path('service-details/',views.service_details),
    path('edit-profile/',views.edit_profile),
    path('logout/',views.logout),
    path('delete-account/',views.delete_account),
    path('feedback/',views.feedback),
    path('upload_pdf/', views.upload_resume),
    path('gemini-interview/', views.gemini_interview),
    path('save-interview-answer/', views.save_interview_answer),
    path('gemini-audio-question/', views.gemini_audio_question),
    path('result/',views.result),  
    path('download-report/',views.download), 
    path('check/',views.check), 
    path('history/',views.history),
    path('history/download-history/',views.download_history),
]
urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)