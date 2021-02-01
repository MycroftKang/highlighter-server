from django.contrib import admin
from highlighter_api import models

admin.site.register(models.Video)
admin.site.register(models.HighlightRange)
admin.site.register(models.UserVote)
