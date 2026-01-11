from django.conf import settings
from django.db.models import Case, When
from .search import SearchService
from .models import Tool
import json
from google import genai
from google.genai import types

class AIService:
    @staticmethod
    def generate_tool_suggestions(user_prompt):
        """
        Uses Gemini to recommend tools based on user prompt and vector search context.
        Returns a list of Tool objects.
        """
        if not settings.GEMINI_API_KEY:
            # Fallback if no key (for dev/testing without key)
            print("No GEMINI_API_KEY found. Returning semantic search results directly.")
            tool_ids = SearchService.search(user_prompt, n_results=5)
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(tool_ids)])
            return Tool.objects.filter(id__in=tool_ids).order_by(preserved)

        # 1. Semantic Search for Context
        tool_ids = SearchService.search(user_prompt, n_results=15)
        tools = Tool.objects.filter(id__in=tool_ids).prefetch_related('translations')
        
        if not tools:
            return []

        # 2. Prepare Context for LLM
        tools_context = []
        for tool in tools:
            trans = tool.get_translation('en')
            desc = trans.short_description if trans else ""
            tools_context.append(f"- {tool.name} (slug: {tool.slug}): {desc}")
        
        context_str = "\n".join(tools_context)
        
        # 3. Call Gemini
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        system_instruction = """
        You are an expert AI software architect.
        User will provide a description of their workflow or profession.
        
        Your task:
        1. Analyze the intent and identify 3-6 most relevant software tools.
        2. Generate a creative, short, professional Title for this tool stack (e.g. 'Freelance Video Editor Kit').
        3. Generate a concise 1-sentence Description of what this stack helps achieve.
        4. Select tools that exist in the real world (e.g. Slack, Trello, PyCharm, Adobe Premiere).
        
        Output MUST be valid JSON with this exact structure:
        {
            "title": "Creative Stack Title",
            "description": "A brief description of this stack.",
            "tools": ["tool_slug_1", "tool_slug_2", "tool_slug_3"]
        }
        
        Important:
        - Return ONLY the JSON. No markdown formatting.
        - Use slugs for tools (lowercase, dashes).
        - If you don't know the exact slug, guess the most likely one (e.g. 'adobe-premiere-pro').
        """

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                ),
                contents=[f"Context matching tools:\n{context_str}\n\nUser Prompt: {user_prompt}"]
            )
            
            # 4. Parse Response
            data = json.loads(response.text)
            
            # Handle potential variations in AI output
            slugs = data.get('tools', []) if isinstance(data, dict) else []
            title = data.get('title', 'Custom Stack')
            description = data.get('description', '')
            
            # 5. Return Tool Objects and Metadata
            selected_tools = Tool.objects.filter(slug__in=slugs, status='published')
            
            return {
                'tools': selected_tools,
                'title': title,
                'description': description
            }
            
        except Exception as e:
            print(f"AI Error: {e}")
            # Fallback to simple search results
            return {
                'tools': tools[:5],
                'title': 'Suggested Tools (Fallback)',
                'description': 'Tools based on semantic search due to AI error.'
            }
