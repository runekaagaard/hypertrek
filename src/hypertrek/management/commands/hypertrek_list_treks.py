from django.core.management.base import BaseCommand, CommandError
from hypertrek import hypertrek

def obj_path(obj):
    return f"{obj.__module__}.{obj.__name__}"

class Command(BaseCommand):
    help = 'List all registered treks.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )

    def handle(self, *args, **options):
        for k, v in hypertrek.TREKS.items():
            print(f"{obj_path(k)}: title='{v['title']}'")

            if options['verbose']:
                for i, mission in enumerate(k()):
                    print(" " * 4, f"{i+1}.", obj_path(mission))
