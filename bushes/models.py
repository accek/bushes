from django.db import models
from django.contrib.auth.models import User

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

class Sentence(models.Model):
    identifier = models.CharField(max_length=255)
    text = models.TextField()
    tokens_json = models.TextField()
    priority = models.IntegerField(default=100)

    class Meta:
        ordering = ('-priority', 'id')

    def __unicode__(self):
        return smart_truncate(self.text, 100)

class Assignment(models.Model):
    sentence = models.ForeignKey(Sentence, related_name='assignments')
    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    tree_json = models.TextField(blank=True)
    latest_tree = models.ForeignKey('Tree', blank=True, null=True,
            related_name='latest_for_assignment')

    def __unicode__(self):
        return u'[%d/%d/%s] %s' % (self.id, self.sentence_id,
                self.user.username, self.sentence)

class Tree(models.Model):
    assignment = models.ForeignKey(Assignment)
    date = models.DateTimeField(auto_now_add=True)
    tree_json = models.TextField()

    def __unicode__(self):
        return u'[%d/%d/%d/%s] %s' % (self.id, self.assignment_id,
                self.assignment.sentence_id, self.assignment.user.username,
                self.assignment.sentence)
