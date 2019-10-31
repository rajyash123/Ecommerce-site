from django.core.management.base import BaseCommand
import os

# adding command
class Command(BaseCommand):
    help = 'Renames a django Project'

    def add_arguments(self, parser):
        parser.add_argument('new_project_name', type=str, help='The new Django Project')

    def handle(self, *args, **options):
        new_project_name = options['new_project_name']

        # bit of logic to rename the project

        files_to_rename = ['demo/settings/base.py', 'demo/wsgi.py', 'manage.py']
        folder_to_rename = 'demo'

        for f in files_to_rename:
            with open(f, 'r') as file:
                filedata = file.read()

            filedata = filedata.replace('demo',new_project_name)

            with open(f, 'w') as file:
                file.write(filedata)
        os.rename(folder_to_rename)

        self.stdout.write(self.style.SUCCESS('Project has been renamed to %s' % new_project_name))
