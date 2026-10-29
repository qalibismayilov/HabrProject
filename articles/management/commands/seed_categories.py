
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from articles.models import Category


CATEGORIES = [
    ("Backend", "backend"),
    ("Frontend", "frontend"),
    ("AI", "ai"),
    ("Cyber Security", "cyber-security"),
    ("Cyber Sport", "cyber-sport"),
    ("Game Development", "game-development"),
]


class Command(BaseCommand):
    help = "Create the default article categories"

    def handle(self, *args, **options):
        for name, slug in CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Category created: {category.name}"
                    )
                )
            else:
                self.stdout.write(
                    f"Category already exists: {category.name}"
                )

        self.stdout.write(
            self.style.SUCCESS("Category setup completed.")
        )
