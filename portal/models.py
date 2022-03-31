from django.db import models


class Collection(models.Model):
    file_name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField()

    def __str__(self):
        return self.file_name
