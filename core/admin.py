from django.contrib import admin
from .models import User, Club, Publication, Reaction, Challenge, Project, Notification

admin.site.register(User)
admin.site.register(Club)
admin.site.register(Publication)
admin.site.register(Reaction)
admin.site.register(Challenge)
admin.site.register(Project)
admin.site.register(Notification)