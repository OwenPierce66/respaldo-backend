from django.db import models
from django.contrib.auth.models import User

class CommunityPost(models.Model):
    createdBy = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    text = models.TextField()

class CommunityComment(models.Model):
    createdBy = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()

    @property
    def children(self):
        return CommunityComment.objects.filter(parent=self).order_by('-createdAt')

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True
