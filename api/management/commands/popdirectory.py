from django.core.management.base import BaseCommand, CommandError
from api.models import Directory
import random
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "create dummy data in Directory model"


    def handle(self, *args, **options):
        quanity_needed = 100
        nouns = ("puppy", "car", "rabbit", "girl", "monkey")
        verbs = ("runs", "hits", "jumps", "drives", "barfs") 
        adv = ("crazily.", "dutifully.", "foolishly.", "merrily.", "occasionally.")
        adj = ("adorable", "clueless", "dirty", "odd", "stupid")
        while quanity_needed != 0:
          num = random.randrange(0,5)
          Directory.objects.create(
            name = nouns[num] + ' ' + verbs[num] + ' ' + adv[num] + ' ' + adj[num],
            latitude = 30.0104615,
            longitude = -107.564559,
            phone_number = 801-555-5555,
            category = "Random"
          )
          quanity_needed -= 1
        print('Requested Directory items have been created')
