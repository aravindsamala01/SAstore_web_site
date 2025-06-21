from django.core.management.base import BaseCommand
from SAstore.models import Product
import random

class Command(BaseCommand):
    help = 'Assigns random prices between 900 and 1500 to products.'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            product.price = random.randint(900, 1500)
            product.save()
            self.stdout.write(self.style.SUCCESS(f'Set price for {product.name}: ₹{product.price}'))
