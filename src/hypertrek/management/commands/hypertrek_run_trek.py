from django.core.management.base import BaseCommand, CommandError
from hypertrek.prompt import run_trek
import importlib

def obj_path(obj):
    return f"{obj.__module__}.{obj.__name__}"

class Command(BaseCommand):
    help = 'Runs given trek'

    def add_arguments(self, parser):
        parser.add_argument('trek_dotted_path', type=str)

    def handle(self, *args, **options):
        trek_dotted_path = options['trek_dotted_path']
        module_name, trek_name = trek_dotted_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        trek = getattr(module, trek_name)
        run_trek(trek())
