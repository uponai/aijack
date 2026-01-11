from django.core.management.base import BaseCommand
from tools.models import Tool, ToolStack
from tools.search import SearchService

class Command(BaseCommand):
    help = 'Re-index all tools and stacks into Vector DB'

    def handle(self, *args, **options):
        self.stdout.write('Indexing tools...')
        tools = Tool.objects.filter(status='published')
        count_tools = SearchService.add_tools(tools)
        self.stdout.write(self.style.SUCCESS(f'Indexed {count_tools} tools.'))
        
        self.stdout.write('Indexing stacks...')
        stacks = ToolStack.objects.all()
        count_stacks = SearchService.add_stacks(stacks)
        self.stdout.write(self.style.SUCCESS(f'Indexed {count_stacks} stacks.'))
