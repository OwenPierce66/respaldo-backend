# newforum/models.py
from django.db import models
from django.contrib.auth.models import User

class NewCommunityPost(models.Model):
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    text = models.TextField()

class NewCommunityComment(models.Model):
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(NewCommunityPost, on_delete=models.CASCADE)
    text = models.TextField()

    @property
    def children(self):
        return NewCommunityComment.objects.filter(parent=self).order_by('-createdAt')

    @property
    def is_parent(self):
        return self.parent is None
