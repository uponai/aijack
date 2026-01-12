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
                model="gemini-flash-lite-latest", 
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

    @staticmethod
    def generate_workflow_description(stack_name, tools_list):
        """
        Generates a step-by-step workflow description for a given stack.
        """
        if not settings.GEMINI_API_KEY:
            return "Workflow description unavailable (No API Key)."
        
        # Prepare context
        tools_context = []
        for tool in tools_list:
            trans = tool.get_translation('en')
            desc = trans.short_description if trans else ""
            tools_context.append(f"- {tool.name}: {desc}")
        
        context_str = "\n".join(tools_context)
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        system_instruction = """
        You are an expert AI software architect.
        User will provide a Stack Name and a list of Tools.
        
        Your task:
        Create a practical, step-by-step workflow description explaining how these tools work together to solve a problem.
        
        Guidelines:
        - Do not add title
        - Start with a brief overview.
        - Use numbered steps (1., 2., 3.).
        - Focus on integration and data flow between the tools.
        - Be professional but engaging.
        - Keep it under 200 words.
        - Used markdown formatting.
        """
        
        prompt = f"Stack Name: {stack_name}\n\nTools:\n{context_str}"
        
        try:
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                ),
                contents=[prompt]
            )
            return response.text
        except Exception as e:
            print(f"AI Workflow Gen Error: {e}")
            return "Could not generate workflow description at this time."

    @staticmethod
    def generate_tool_metadata(tool_name, website_url, short_description, long_description, 
                                pricing_text, existing_categories, existing_professions, existing_tags):
        """
        Uses Gemini to generate complete tool metadata for bulk import.
        Returns a dictionary with all required fields.
        """
        if not settings.GEMINI_API_KEY:
            return {
                'error': 'No API key configured',
                'pricing_type': 'freemium',
                'category_names': [],
                'profession_names': [],
                'tag_names': [],
                'meta_title': tool_name,
                'meta_description': short_description[:160] if short_description else '',
                'use_cases': '',
                'pros': '',
                'cons': ''
            }
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Build context with existing entities
        categories_list = ", ".join(existing_categories) if existing_categories else "None yet"
        professions_list = ", ".join(existing_professions) if existing_professions else "None yet"
        tags_list = ", ".join(existing_tags) if existing_tags else "None yet"
        
        system_instruction = """
You are an expert AI tools curator and SEO specialist.
You will receive information about an AI tool and must generate comprehensive metadata.

Your task is to analyze the tool and produce:
1. pricing_type: Exactly one of: "free", "freemium", or "paid"
   - "free" = completely free, no paid tiers
   - "freemium" = has free tier plus paid options
   - "paid" = requires payment, may have trial

2. category_names: 1-3 relevant categories. Prefer existing ones, but suggest new if needed.

3. profession_names: 1-4 target professions who would use this tool. Prefer existing ones.

4. tag_names: 3-6 feature tags (e.g., "AI-powered", "automation", "cloud-based"). Prefer existing ones.

5. meta_title: SEO title, 50-60 characters. Include tool name and key benefit.

6. meta_description: SEO description, 150-160 characters. Compelling summary with call to action.

7. use_cases: 3-5 specific use cases, comma-separated. Be practical and specific.

8. pros: 3-5 advantages of this tool, comma-separated. Be specific and value-focused.

9. cons: 2-3 potential downsides or limitations, comma-separated. Be honest but fair.

Output MUST be valid JSON only. No markdown, no explanation.
"""

        prompt = f"""
TOOL INFORMATION:
- Name: {tool_name}
- Website: {website_url}
- Short Description: {short_description}
- Detailed Description: {long_description}
- Pricing Info from CSV: {pricing_text}

EXISTING SYSTEM DATA (prefer these when applicable):
- Categories: {categories_list}
- Professions: {professions_list}
- Tags: {tags_list}

Generate the complete metadata JSON for this tool.
"""

        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                ),
                contents=[prompt]
            )
            
            data = json.loads(response.text)
            
            # Validate and normalize response
            result = {
                'pricing_type': data.get('pricing_type', 'freemium'),
                'category_names': data.get('category_names', []),
                'profession_names': data.get('profession_names', []),
                'tag_names': data.get('tag_names', []),
                'meta_title': data.get('meta_title', tool_name)[:200],
                'meta_description': data.get('meta_description', short_description[:160] if short_description else ''),
                'use_cases': data.get('use_cases', ''),
                'pros': data.get('pros', ''),
                'cons': data.get('cons', '')
            }
            
            # Ensure pricing_type is valid
            if result['pricing_type'] not in ['free', 'freemium', 'paid']:
                result['pricing_type'] = 'freemium'
            
            # Convert lists to comma-separated if needed
            if isinstance(result['use_cases'], list):
                result['use_cases'] = ', '.join(result['use_cases'])
            if isinstance(result['pros'], list):
                result['pros'] = ', '.join(result['pros'])
            if isinstance(result['cons'], list):
                result['cons'] = ', '.join(result['cons'])
            
            return result
            
        except Exception as e:
            print(f"AI Metadata Gen Error: {e}")
            # Return sensible defaults
            return {
                'error': str(e),
                'pricing_type': 'freemium',
                'category_names': [],
                'profession_names': [],
                'tag_names': [],
                'meta_title': tool_name,
                'meta_description': short_description[:160] if short_description else '',
                'use_cases': '',
                'pros': '',
                'cons': ''
            }
