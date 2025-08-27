from django.core.management.base import BaseCommand, CommandError
from api.models import Blog
import random
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "create dummy data in Blog model"


    def handle(self, *args, **options):
        quanity_needed = 100
        nouns = ("puppy", "car", "rabbit", "girl", "monkey")
        verbs = ("runs", "hits", "jumps", "drives", "barfs") 
        adv = ("crazily.", "dutifully.", "foolishly.", "merrily.", "occasionally.")
        adj = ("adorable", "clueless", "dirty", "odd", "stupid")
        while quanity_needed != 0:
          num = random.randrange(0,5)
          Blog.objects.create(
            title = nouns[num] + ' ' + verbs[num] + ' ' + adv[num] + ' ' + adj[num],
            summary = nouns[num] + ' ' + verbs[num] + ' ' + adv[num] + ' ' + adj[num] + "." + nouns[num] + ' ' + verbs[num] + ' ' + adv[num] + ' ' + adj[num] + ".",
            thumb_nail = "http://placekitten.com/100/100",
            createdBy = User.objects.get(id=1),
            lastUpdatedBy = User.objects.get(id=1),
          )

          quanity_needed -= 1
        print('Requested BLOG posts have been created')
