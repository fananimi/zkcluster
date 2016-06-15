from django.contrib import admin

from .models import Terminal, User, Attendance

admin.site.register(Terminal)
admin.site.register(User)
admin.site.register(Attendance)
