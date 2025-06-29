from django.db.models.signals import post_migrate
from django.dispatch import receiver
from backoffice_engine.models import Plandetail


@receiver(post_migrate)
def create_default_plans(sender, **kwargs):
    if sender.name != 'backoffice_engine':
        return

    default_plans = [
        {"name": "Free Plan", "description": "Basic access", "price": 0, "duration_days": 30, "credits": 10},
        {"name": "Silver Plan", "description": "Access to premium features", "price": 499, "duration_days": 30, "credits": 20},
        {"name": "Gold Plan", "description": "Extended features and support", "price": 999, "duration_days": 90, "credits": 30},
        {"name": "Diamond Plan", "description": "All features with priority support", "price": 1999, "duration_days": 180, "credits": 40},
        {"name": "Platinum Plan", "description": "Most Expensive Plan", "price": 50000,"duration_days": 365, "credits": 100},

    ]

    for plan in default_plans:
        print(f"{plan['name']}")
        Plandetail.objects.get_or_create(name=plan["name"], defaults=plan)