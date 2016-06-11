from django.contrib import admin

from .models import Terminal, User, UIDCounter, DeletedUID

admin.site.register(Terminal)
admin.site.register(DeletedUID)
admin.site.register(UIDCounter)
admin.site.register(User)
