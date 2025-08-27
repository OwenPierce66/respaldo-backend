from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from api.models import Listing
import random

class Command(BaseCommand):
    help = "create dummy data in Listing model"


    def handle(self, *args, **options):
        quanity_needed = 15
        while quanity_needed != 0:
            listing = Listing.objects.create(
              user = User.objects.get(id=1),
              contact_email = "mansourijaxson@gmail.com",
              contact_number = "801-555-5555",
              category = 23,
              condition = 1,
              description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
              location = "Riverton, UT",
              price = 3000,
              title = "Lorem ipsum dolor sit"
            )
            listing.photos.add(1, 2, 3, 4)
            listing.save()
            quanity_needed =- 1
        print('Requested posts have been created')
