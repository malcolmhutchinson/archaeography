from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Address)
admin.site.register(Member)
admin.site.register(Organisation)
admin.site.register(Person)
