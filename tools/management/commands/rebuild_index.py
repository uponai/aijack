from django.core.management.base import BaseCommand
from tools.models import Tool
from tools.search import SearchService

class Command(BaseCommand):
    help = 'Rebuilds the semantic search index'

    def handle(self, *args, **options):
        self.stdout.write('Initializing embedding model (this may take a moment)...')
        # Trigger model load
        SearchService.get_model()
        
        self.stdout.write('Fetching tools...')
        tools = Tool.objects.filter(status='published').prefetch_related('translations', 'tags')
        count = tools.count()
        
        self.stdout.write(f'Found {count} tools. Generating embeddings and indexing...')
        
        # Process in batches if necessary, but for 36 tools, one batch is fine
        added_count = SearchService.add_tools(tools)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully indexed {added_count} tools.'))
