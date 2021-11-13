from django.contrib import admin
from .models import Result, User, Blacklist

# Register your models here.
admin.site.register(Result)
admin.site.register(User)
admin.site.register(Blacklist)
