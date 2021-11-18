from django.contrib import admin
from .models import Result, User, Blacklist, User_search_count

# Register your models here.
admin.site.register(Result)
admin.site.register(User)
admin.site.register(Blacklist)
admin.site.register(User_search_count)