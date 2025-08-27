from django.core.management.base import BaseCommand, CommandError
from api.models import Post, Item
import random

class Command(BaseCommand):
    help = "create dummy data in Post model"


    def handle(self, *args, **options):
        posts_needed = 140
        posts = [
            {
                "post_type": "ad",
                "title": "German's Barbershop",
                "content": None,
                "contact": "123-456-7890",
            },
            {
                "post_type": "blog",
                "title": "THE RUSSIANS ARE INVADING",
                "content": "runnnnnnnnnnnnnnnnnnn nnnnnnnnnnnnnnnnnnnnnnnnnnnnnn nnn n n n  n n n n n n n n nnnnnnnnnnnnnnnnnn",
                "contact": "123-456-7890",
            },
            {
                "post_type": "announcement",
                "title": "2021 Fair's Committee Meeting",
                "content": "We will be gathering on wednesday this week to discuss on what day we wil release the  B E E S",
                "contact": None,
            },
        ]

        while posts_needed != 0:
            post = random.choice(posts)
            print(post["post_type"])
            post = Post.objects.create(
                post_type = post["post_type"],
                title = post["title"],
                content = post["content"],
                contact = post["contact"]
            )
            print(post)
            posts_needed -= 1
        print('Posts created')
