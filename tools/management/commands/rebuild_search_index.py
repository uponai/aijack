from django.core.management.base import BaseCommand
from tools.models import Tool, ToolStack, Profession
from tools.search import SearchService

class Command(BaseCommand):
    help = 'Rebuild or reindex the semantic search index'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear the index before reindexing',
        )
        parser.add_argument(
            '--models',
            nargs='+',
            default=['tools', 'stacks', 'professions'],
            help='Specify which models to index (tools, stacks, professions)',
        )

    def handle(self, *args, **options):
        models = options['models']
        clear = options['clear']
        
        valid_models = {'tools', 'stacks', 'professions'}
        target_models = [m for m in models if m in valid_models]
        
        if not target_models:
            self.stdout.write(self.style.ERROR(f'No valid models specified. Choose from: {valid_models}'))
            return

        if clear:
            self.stdout.write(f'Clearing index for: {target_models}...')
            SearchService.clear_index(target_models)
            self.stdout.write(self.style.SUCCESS('Index cleared.'))

        if 'tools' in target_models:
            self.stdout.write('Indexing tools...')
            tools = Tool.objects.filter(status='published').prefetch_related('translations', 'tags')
            count = SearchService.add_tools(tools)
            self.stdout.write(self.style.SUCCESS(f'Indexed {count} tools.'))

        if 'stacks' in target_models:
            self.stdout.write('Indexing stacks...')
            stacks = ToolStack.objects.all().prefetch_related('tools')
            count = SearchService.add_stacks(stacks)
            self.stdout.write(self.style.SUCCESS(f'Indexed {count} stacks.'))

        if 'professions' in target_models:
            self.stdout.write('Indexing professions...')
            professions = Profession.objects.all()
            count = SearchService.add_professions(professions)
            self.stdout.write(self.style.SUCCESS(f'Indexed {count} professions.'))
