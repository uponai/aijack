from django.conf import settings
from django.db.models import Case, When
from .search import SearchService
from .models import Tool, Profession, ToolStack
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
You have access to Google Search. Use it to verify the tool's existence, latest pricing, and features if the provided info is sparse.

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

Generate the complete metadata JSON for this tool. Use search to verify details.
"""

        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    # Note: response_mime_type cannot be used with tools
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                ),
                contents=[prompt]
            )
            
            # Extract JSON from response text (API returns text when using tools)
            response_text = response.text.strip()
            
            # Try to find JSON in the response (may be wrapped in markdown or extra text)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                # If no JSON found, try parsing the entire response
                data = json.loads(response_text)
            
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
    @staticmethod
    def complete_tool_fields(tool_data, existing_categories, existing_professions, existing_tags):
        """
        Complete missing fields for a tool using AI based on existing data.
        tool_data: dict with current tool information
        Returns: dict with completed fields
        """
        if not settings.GEMINI_API_KEY:
            return {'error': 'No API key configured'}
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Build context
        categories_list = ", ".join(existing_categories) if existing_categories else "None yet"
        professions_list = ", ".join(existing_professions) if existing_professions else "None yet"
        tags_list = ", ".join(existing_tags) if existing_tags else "None yet"

        # Semantic Search for related context (optional but helpful)
        search_query = f"{tool_data.get('name')} {tool_data.get('short_description', '')}"
        
        # Find relevant professions via vector search
        try:
            prof_ids = SearchService.search(search_query, n_results=10, collection_name="professions")
            semantic_profs = list(Profession.objects.filter(id__in=prof_ids).values_list('name', flat=True))
            if semantic_profs:
                 # prioritize semantic matches
                professions_list = ", ".join(semantic_profs + [p for p in existing_professions if p not in semantic_profs])
        except Exception as e:
            print(f"Vector search failed (professions): {e}")

        system_instruction = """
You are an AI tools curator helping complete tool information.

Review the provided information. Complete missing fields AND augment existing lists (Categories, Professions, Tags) if they are incomplete or could be improved with more relevant items.

Fields to complete/improve:
- pricing_type, category_names (2-4 relevant), profession_names (3-6 relevant target), tag_names (5-10 feature tags)
- meta_title, meta_description
- short_description, long_description
- use_cases, pros, cons

Output valid JSON only with completed fields.
"""

        prompt = f"""
TOOL: {tool_data.get('name')}
Website: {tool_data.get('website_url', '')}
Short Desc: {tool_data.get('short_description', '(MISSING)')}
Long Desc: {tool_data.get('long_description', '(MISSING)')}
Pricing: {tool_data.get('pricing_type', '(MISSING)')}
Categories: {tool_data.get('categories', '(MISSING)')}
Professions: {tool_data.get('professions', '(MISSING)')}
Tags: {tool_data.get('tags', '(MISSING)')}
Meta Title: {tool_data.get('meta_title', '(MISSING)')}
Meta Desc: {tool_data.get('meta_description', '(MISSING)')}
Use Cases: {tool_data.get('use_cases', '(MISSING)')}
Pros: {tool_data.get('pros', '(MISSING)')}
Cons: {tool_data.get('cons', '(MISSING)')}

EXISTING: Categories: {categories_list} | Professions: {professions_list} | Tags: {tags_list}

Complete missing fields and suggest additional relevant items for categories, professions, and tags to improve coverage.
"""

        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                ),
                contents=[prompt]
            )
            
            response_text = response.text.strip()
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = json.loads(json_match.group(0) if json_match else response_text)
            
            result = {}
            for key in ['pricing_type', 'category_names', 'profession_names', 'tag_names',
                       'meta_title', 'meta_description', 'short_description', 'long_description']:
                if key in data:
                    result[key] = data[key]
            
            for key in ['use_cases', 'pros', 'cons']:
                if key in data:
                    result[key] = data[key] if isinstance(data[key], str) else ', '.join(data[key])
            
            return result
        except Exception as e:
            print(f"AI Complete Tool Error: {e}")
            return {'error': str(e)}

    @staticmethod
    def complete_stack_fields(stack_data, existing_professions, available_tools):
        """
        Complete missing fields for a stack using AI.
        stack_data: dict with current stack information
        available_tools: list of tool names available in system
        Returns: dict with completed fields
        """
        if not settings.GEMINI_API_KEY:
            return {'error': 'No API key configured'}
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Semantic Search for context
        search_query = f"{stack_data.get('name')} {stack_data.get('description', '')}"
        
        professions_str = "None yet"
        tools_str = "None yet"
        
        try:
            # 1. Find relevant Tools
            tool_ids = SearchService.search(search_query, n_results=20, collection_name="tools")
            semantic_tools = list(Tool.objects.filter(id__in=tool_ids).values_list('name', flat=True))
            
            # Combine dict-provided available tools (which might be comprehensive) with semantic ones
            # We want semantic ones first or highlighted
            all_tools = semantic_tools + [t for t in available_tools if t not in semantic_tools]
            tools_str = ", ".join(all_tools[:60]) # Limit context size
            
            # 2. Find relevant Professions
            prof_ids = SearchService.search(search_query, n_results=10, collection_name="professions")
            semantic_profs = list(Profession.objects.filter(id__in=prof_ids).values_list('name', flat=True))
            all_profs = semantic_profs + [p for p in existing_professions if p not in semantic_profs]
            professions_str = ", ".join(all_profs)
            
        except Exception as e:
            print(f"Vector search failed (stack): {e}")
            professions_str = ", ".join(existing_professions) if existing_professions else "None yet"
            tools_str = ", ".join(available_tools[:50]) if available_tools else "None yet"
        
        system_instruction = """
You are an AI workflow architect helping complete missing information for tool stack entries.

A stack is a curated bundle of AI tools that work together to solve a specific workflow.

Review the provided information. Complete missing fields AND augment existing tool/profession lists if they can be improved with more relevant items. Use Google Search to verify.

Fields to complete/improve:
- tagline: Catchy one-liner (max 200 chars)
- description: Detailed explanation of the stack's purpose and value
- workflow_description: Step-by-step markdown guide on how the tools work together
- tool_names: List of 5-18 relevant tools from the AVAILABLE TOOLS list (prefer existing tools)
- profession_names: List of 3-6 relevant professions from the EXISTING PROFESSIONS list (prefer existing professions)
- meta_title: SEO title (50-60 chars)
- meta_description: SEO description (150-160 chars)

For workflow_description, create a professional step-by-step guide in markdown with:
- Brief overview paragraph
- Numbered steps (1., 2., 3., etc.)
- Focus on integration and data flow between tools
- Be specific about what each tool does in the workflow

Output valid JSON only with completed fields.
"""

        prompt = f"""
STACK: {stack_data.get('name')}
Tagline: {stack_data.get('tagline', '(MISSING)')}
Description: {stack_data.get('description', '(MISSING)')}
Workflow: {stack_data.get('workflow_description', '(MISSING)')}
Current Tools: {stack_data.get('tools', '(MISSING)')}
Professions: {stack_data.get('professions', '(MISSING)')}
Meta Title: {stack_data.get('meta_title', '(MISSING)')}
Meta Desc: {stack_data.get('meta_description', '(MISSING)')}

Meta Desc: {stack_data.get('meta_description', '(MISSING)')}

RELEVANT TOOLS (Semantic & Available): {tools_str}
RELEVANT PROFESSIONS (Semantic & Available): {professions_str}

Complete missing fields. Suggest relevant tools and professions from the provided lists.
"""

        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                ),
                contents=[prompt]
            )
            
            response_text = response.text.strip()
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = json.loads(json_match.group(0) if json_match else response_text)
            
            result = {}
            for key in ['tagline', 'description', 'workflow_description', 'tool_names', 
                       'profession_names', 'meta_title', 'meta_description']:
                if key in data:
                    result[key] = data[key]
            
            return result
        except Exception as e:
            print(f"AI Complete Stack Error: {e}")
            return {'error': str(e)}

    @staticmethod
    def complete_profession_fields(profession_data, available_tools, available_stacks):
        """
        Complete missing fields for a profession using AI.
        profession_data: dict with current profession information
        available_tools: list of tool names available in system
        available_stacks: list of stack names available in system
        Returns: dict with completed fields
        """
        if not settings.GEMINI_API_KEY:
            return {'error': 'No API key configured'}
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        
        # Semantic Search for context
        search_query = f"{profession_data.get('name')} {profession_data.get('description', '')}"
        
        tools_str = "None yet"
        stacks_str = "None yet"
        
        try:
            # 1. Find relevant Tools
            tool_ids = SearchService.search(search_query, n_results=25, collection_name="tools")
            semantic_tools = list(Tool.objects.filter(id__in=tool_ids).values_list('name', flat=True))
            all_tools = semantic_tools + [t for t in available_tools if t not in semantic_tools]
            tools_str = ", ".join(all_tools[:80])
            
            # 2. Find relevant Stacks
            stack_ids = SearchService.search(search_query, n_results=10, collection_name="stacks")
            semantic_stacks = list(ToolStack.objects.filter(id__in=stack_ids).values_list('name', flat=True))
            all_stacks = semantic_stacks + [s for s in available_stacks if s not in semantic_stacks]
            stacks_str = ", ".join(all_stacks[:40])
            
        except Exception as e:
             print(f"Vector search failed (profession): {e}")
             tools_str = ", ".join(available_tools[:100]) if available_tools else "None yet"
             stacks_str = ", ".join(available_stacks[:50]) if available_stacks else "None yet"
        
        system_instruction = """
You are an AI career expert helping complete missing information for profession entries.

Review the provided information. Complete missing fields AND augment existing tool/stack lists if they can be improved with more relevant items. Use Google Search to verify.

Fields to complete/improve:
- description: Detailed explanation of the profession (what they do, typical responsibilities)
- hero_tagline: Catchy one-liner that captures the essence of this profession (max 100 chars)
- icon: Font Awesome icon class (e.g., "fa-solid fa-code", "fa-solid fa-user-doctor")
- meta_title: SEO title (50-60 chars)
- meta_description: SEO description (150-160 chars)
- tool_names: List of 13-18 relevant tools from the AVAILABLE TOOLS list (prefer existing tools)
- stack_names: List of 5-8 relevant stacks from the AVAILABLE STACKS list (prefer existing stacks)

Output valid JSON only with completed fields.
"""

        prompt = f"""
PROFESSION: {profession_data.get('name')}
Description: {profession_data.get('description', '(MISSING)')}
Tagline: {profession_data.get('hero_tagline', '(MISSING)')}
Icon: {profession_data.get('icon', '(MISSING)')}
Meta Title: {profession_data.get('meta_title', '(MISSING)')}
Meta Desc: {profession_data.get('meta_description', '(MISSING)')}

AVAILABLE TOOLS (Semantic & Available): {tools_str}
AVAILABLE STACKS (Semantic & Available): {stacks_str}

Complete missing fields. Suggest additional relevant tools and stacks to improve the profession's profile.
"""

        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                ),
                contents=[prompt]
            )
            
            response_text = response.text.strip()
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = json.loads(json_match.group(0) if json_match else response_text)
            
            result = {}
            for key in ['description', 'hero_tagline', 'icon', 'meta_title', 'meta_description', 'tool_names', 'stack_names']:
                if key in data:
                    result[key] = data[key]
            
            return result
        except Exception as e:
            print(f"AI Complete Profession Error: {e}")
            return {'error': str(e)}
