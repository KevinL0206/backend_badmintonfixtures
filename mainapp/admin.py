from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(club)
admin.site.register(player)
admin.site.register(match)
admin.site.register(session)