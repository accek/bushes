from django.db import models
from django.contrib.auth.models import User

class Sentence(models.Model):
    filename = models.CharField(max_length=255)
    xml_id = models.CharField(max_length=255)
    text = models.TextField()
    tokens_json = models.TextField()

class Assignment(models.Model):
    sentence = models.ForeignKey(Sentence)
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    tree_json = models.TextField(blank=True)
