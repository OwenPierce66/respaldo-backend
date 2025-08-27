from django.core.management.base import BaseCommand, CommandError
from api.models import Post

class Command(BaseCommand):
    help = "delete all posts, only to be done in development"

    def handle(self, *args, **options):
        Post.objects.all().delete()
        print('All posts deleted')