from django.contrib import admin
from backoffice_engine.models import User,Plandetail,Subscription,Feedback,Profile,Interview,InterviewResult

# Register your models here.
admin.site.register(User)
admin.site.register(Plandetail)
admin.site.register(Subscription)
admin.site.register(Feedback)
admin.site.register(Profile)
admin.site.register(Interview)
admin.site.register(InterviewResult)