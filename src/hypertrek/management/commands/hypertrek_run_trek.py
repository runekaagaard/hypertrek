from django.core.management.base import BaseCommand, CommandError
from hypergen_first_app.treks import example_trek
from hypertrek.prompt import run_trek

def obj_path(obj):
    return f"{obj.__module__}.{obj.__name__}"

class Command(BaseCommand):
    help = 'Runs given trek'

    def handle(self, *args, **options):
        run_trek(example_trek())
