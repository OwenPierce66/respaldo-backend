from django.core.management.base import BaseCommand, CommandError
from api.models import Post, Item
import random

class Command(BaseCommand):
    help = "create dummy data in Post model"


    def handle(self, *args, **options):
        quanity_needed = 15
        items = Item.objects.all().order_by('id')
        type_options = ('blog', 'ad', 'announcement')

        titles = ('Big News', "New Thing", "Top story", "Best Deal")

        while quanity_needed != 0:
            random_item = random.choice(items)
            random_type = random.choice(type_options)
            post = Post.objects.create(
                post_type = random_type,
                title = random.choice(titles),
                content = "Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content Content",
                contact = "Jaxson Mansouri"
            )
            post.items.add(random_item)
            post.save()
            quanity_needed -= 1
        print('Requested posts have been created')
