from django.core.management.base import BaseCommand
from tools.models import Category, Profession, Tag, Tool, ToolTranslation, ToolStack

class Command(BaseCommand):
    help = 'Seeds the database with extended sample data (30+ tools, 15+ professions)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding extended data...')
        
        # --- 1. Professions ---
        professions_data = [
            # Existing (Update icons if needed)
            {'name': 'Architect', 'slug': 'architect', 'icon': 'fa-solid fa-compass-drafting', 'hero_tagline': 'Design smarter structures with AI'},
            {'name': 'Designer', 'slug': 'designer', 'icon': 'fa-solid fa-palette', 'hero_tagline': 'Amplify your creativity with generative AI'},
            {'name': 'Marketer', 'slug': 'marketer', 'icon': 'fa-solid fa-bullhorn', 'hero_tagline': 'Boost reach and conversion with AI insights'},
            {'name': 'Developer', 'slug': 'developer', 'icon': 'fa-solid fa-code', 'hero_tagline': 'Build software faster than ever'},
            {'name': 'Writer', 'slug': 'writer', 'icon': 'fa-solid fa-pen-nib', 'hero_tagline': 'Enhance your storytelling with AI assistants'},
            {'name': 'Entrepreneur', 'slug': 'entrepreneur', 'icon': 'fa-solid fa-rocket', 'hero_tagline': 'Scale your vision with AI automation'},
            
            # New Professions
            {'name': 'HR Manager', 'slug': 'hr-manager', 'icon': 'fa-solid fa-people-arrows', 'hero_tagline': 'Streamline recruitment and employee engagement'},
            {'name': 'Sales Representative', 'slug': 'sales-rep', 'icon': 'fa-solid fa-hand-holding-dollar', 'hero_tagline': 'Close more deals with intelligent insights'},
            {'name': 'Data Scientist', 'slug': 'data-scientist', 'icon': 'fa-solid fa-chart-network', 'hero_tagline': 'Analyze complex data with advanced AI models'},
            {'name': 'Educator', 'slug': 'educator', 'icon': 'fa-solid fa-chalkboard-user', 'hero_tagline': 'Personalize learning and automate grading'},
            {'name': 'Student', 'slug': 'student', 'icon': 'fa-solid fa-graduation-cap', 'hero_tagline': 'Study smarter and research faster'},
            {'name': 'Legal Professional', 'slug': 'legal-pro', 'icon': 'fa-solid fa-scale-balanced', 'hero_tagline': 'Automate contract review and legal research'},
            {'name': 'Healthcare Professional', 'slug': 'healthcare-pro', 'icon': 'fa-solid fa-user-doctor', 'hero_tagline': 'Improve patient care with AI scribes and diagnostics'},
            {'name': 'Real Estate Agent', 'slug': 'real-estate-agent', 'icon': 'fa-solid fa-house-chimney', 'hero_tagline': 'Optimize listings and client management'},
            {'name': 'Game Developer', 'slug': 'game-dev', 'icon': 'fa-solid fa-gamepad', 'hero_tagline': 'Generate assets and NPCs with AI'},
            {'name': 'Musician', 'slug': 'musician', 'icon': 'fa-solid fa-music', 'hero_tagline': 'Compose and master tracks with AI tools'},
            {'name': 'Videographer', 'slug': 'videographer', 'icon': 'fa-solid fa-video', 'hero_tagline': 'Edit and generate video content instantly'},
        ]
        
        professions = {}
        for data in professions_data:
            prof, _ = Profession.objects.update_or_create(slug=data['slug'], defaults=data)
            professions[data['slug']] = prof
            
        self.stdout.write(f'  Managed {len(professions)} professions.')

        # --- 2. Categories ---
        categories_data = [
            {'name': 'Design', 'slug': 'design', 'icon': 'fa-solid fa-palette'},
            {'name': 'Automation', 'slug': 'automation', 'icon': 'fa-solid fa-robot'},
            {'name': 'Content', 'slug': 'content', 'icon': 'fa-solid fa-file-lines'},
            {'name': 'Analytics', 'slug': 'analytics', 'icon': 'fa-solid fa-chart-simple'},
            {'name': 'Development', 'slug': 'development', 'icon': 'fa-solid fa-code'},
            {'name': 'Audio/Video', 'slug': 'audio-video', 'icon': 'fa-solid fa-video'},
            {'name': 'Research', 'slug': 'research', 'icon': 'fa-solid fa-magnifying-glass'},
            {'name': 'Legal', 'slug': 'legal', 'icon': 'fa-solid fa-gavel'},
            {'name': 'HR & Recruiting', 'slug': 'hr', 'icon': 'fa-solid fa-users'},
            {'name': 'Sales & CRM', 'slug': 'sales', 'icon': 'fa-solid fa-sack-dollar'},
            {'name': 'Education', 'slug': 'education', 'icon': 'fa-solid fa-school'},
            {'name': 'Healthcare', 'slug': 'healthcare', 'icon': 'fa-solid fa-heart-pulse'},
            {'name': 'Productivity', 'slug': 'productivity', 'icon': 'fa-solid fa-check-double'},
        ]
        
        categories = {}
        for data in categories_data:
            cat, _ = Category.objects.update_or_create(slug=data['slug'], defaults=data)
            categories[data['slug']] = cat

        # --- 3. Tags ---
        tags_list = [
            'contract-analysis', 'recruiting', 'crm', 'medical-scribe', 'grading', 
            'music-generation', '3d-modeling', 'transcription', 'voice-cloning', 
            'meeting-notes', 'study-aid', 'citation', 'data-viz', 'excel', 
            'lead-generation', 'SEO', 'compliance', 'avatar', 'presentation'
        ]
        tags = {}
        for name in tags_list:
            slug = name.lower()
            tag, _ = Tag.objects.update_or_create(slug=slug, defaults={'name': name.replace('-', ' ').title()})
            tags[slug] = tag

        # --- 4. Tools ---
        tools_data = [
            # --- Legal ---
            {
                'name': 'Casetext CoCounsel', 'slug': 'casetext',
                'website_url': 'https://casetext.com', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['legal-pro'], 'categories': ['legal', 'research'],
                'tags': ['contract-analysis', 'citation'],
                'translation': {
                    'short_description': 'AI legal assistant for document review and research.',
                    'long_description': 'CoCounsel uses advanced LLMs to read, understand, and summarize legal documents, conduct research, and even draft correspondence with citation support.',
                    'use_cases': 'Legal research, Document review, Deposition preparation',
                    'pros': 'High accuracy, Trusted by law firms, Secure',
                    'cons': 'Expensive, Specialized use only',
                    'pros_list': ['Specific for law', 'Secure data', 'Citation checks'],
                    'cons_list': ['Enterprise pricing', 'Learning curve']
                }
            },
            {
                'name': 'Ironclad', 'slug': 'ironclad',
                'website_url': 'https://ironcladapp.com', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['legal-pro', 'hr-manager'], 'categories': ['legal', 'automation'],
                'tags': ['contract-analysis', 'compliance'],
                'translation': {
                    'short_description': 'Digital contracting platform with AI intelligence.',
                    'long_description': 'Ironclad AI helps teams generate, negotiate, and analyze contracts faster using AI to flag risks and suggest clauses.',
                    'use_cases': 'Contract lifecycle management, Risk analysis',
                    'pros': 'Streamlines workflows, collaborative',
                    'cons': 'Requires implementation time',
                    'pros_list': ['Workflow automation', 'Risk flagging', 'Collaboration tools'],
                    'cons_list': ['Setup time', 'Cost']
                }
            },
            
            # --- HR ---
            {
                'name': 'Textio', 'slug': 'textio',
                'website_url': 'https://textio.com', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['hr-manager'], 'categories': ['hr'],
                'tags': ['recruiting'],
                'translation': {
                    'short_description': 'AI for unbiased and effective writing in HR.',
                    'long_description': 'Textio guides recruiters and managers to write more inclusive and effective job posts and performance reviews.',
                    'use_cases': 'Job descriptions, Performance reviews, Employer branding',
                    'pros': 'Reduces bias, Improves response rates',
                    'cons': 'Focus is strictly on writing',
                    'pros_list': ['Bias detection', 'Real-time guidance', 'Analytics'],
                    'cons_list': ['Niche focus', 'Subscription']
                }
            },
            {
                'name': 'Paradox', 'slug': 'paradox',
                'website_url': 'https://paradox.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['hr-manager'], 'categories': ['hr', 'automation'],
                'tags': ['recruiting', 'chatbot'],
                'translation': {
                    'short_description': 'Conversational AI for recruiting.',
                    'long_description': 'Olivia by Paradox is an AI assistant that screens candidates, schedules interviews, and answers candidate questions 24/7.',
                    'use_cases': 'High-volume hiring, Interview scheduling',
                    'pros': 'Saves massive time for recruiters, Good candidate experience',
                    'cons': 'Can feel impersonal if not configured well',
                    'pros_list': ['24/7 availability', 'Automated scheduling', 'ATS integration'],
                    'cons_list': ['Impersonal feel', 'Cost']
                }
            },

            # --- Sales ---
            {
                'name': 'Gong', 'slug': 'gong',
                'website_url': 'https://gong.io', 'pricing_type': 'paid', 'is_featured': True,
                'professions': ['sales-rep', 'manager'],
                'categories': ['sales', 'analytics'],
                'tags': ['crm', 'meeting-notes', 'analytics'],
                'translation': {
                    'short_description': 'Revenue intelligence platform analyzing customer interactions.',
                    'long_description': 'Gong records and analyzes sales calls to give insights on deal risks, competitor mentions, and coaching opportunities.',
                    'use_cases': 'Sales coaching, Deal forecasting, Market intelligence',
                    'pros': 'Deep insights, Automatic recording',
                    'cons': 'Privacy considerations',
                    'pros_list': ['Actionable insights', 'Transcript accuracy', 'Integrations'],
                    'cons_list': ['Recording consent', 'Price']
                }
            },
            {
                'name': 'Apollo.ai', 'slug': 'apollo',
                'website_url': 'https://apollo.io', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['sales-rep', 'marketer'],
                'categories': ['sales'],
                'tags': ['lead-generation', 'automation'],
                'translation': {
                    'short_description': 'Sales intelligence and engagement platform.',
                    'long_description': 'Apollo provides a massive database of contacts and uses AI to help you find ideal prospects and write personalized outreach sequences.',
                    'use_cases': 'Cold outreach, Lead enrichment, Sales engagement',
                    'pros': 'Huge database, All-in-one tool',
                    'cons': 'Data quality varies',
                    'pros_list': ['Contact database', 'Email sequencing', 'Chrome extension'],
                    'cons_list': ['Data accuracy', 'UI complexity']
                }
            },

            # --- Healthcare ---
            {
                'name': 'Nabla', 'slug': 'nabla',
                'website_url': 'https://nabla.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['healthcare-pro'],
                'categories': ['healthcare'],
                'tags': ['medical-scribe', 'transcription'],
                'translation': {
                    'short_description': 'AI copilot for doctors to automate clinical documentation.',
                    'long_description': 'Nabla listens to patient consultations and automatically generates structured clinical notes, allowing doctors to focus on the patient.',
                    'use_cases': 'Clinical notes, Patient summaries',
                    'pros': 'Updates in real-time, Privacy focused',
                    'cons': 'Review required',
                    'pros_list': ['Time saving', 'Structured data', 'Secure'],
                    'cons_list': ['Doctor oversight needed', 'Language support']
                }
            },

            # --- Education ---
            {
                'name': 'Khanmigo', 'slug': 'khanmigo',
                'website_url': 'https://khanacademy.org', 'pricing_type': 'paid', 'is_featured': True,
                'professions': ['student', 'educator'],
                'categories': ['education'],
                'tags': ['study-aid', 'chatbot'],
                'translation': {
                    'short_description': 'AI tutor and teaching assistant by Khan Academy.',
                    'long_description': 'Khanmigo guides students through problems without giving the answer and helps teachers create lesson plans.',
                    'use_cases': 'Homework help, Lesson planning, Coding tutor',
                    'pros': 'Safe for students, Pedagogically sound',
                    'cons': 'Paid donation required',
                    'pros_list': ['Socratic method', 'Safe environment', 'Teacher tools'],
                    'cons_list': ['Cost', 'US focus initially']
                }
            },
            {
                'name': 'Gradescope', 'slug': 'gradescope',
                'website_url': 'https://gradescope.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['educator'],
                'categories': ['education', 'automation'],
                'tags': ['grading'],
                'translation': {
                    'short_description': 'AI-assisted grading for higher ed.',
                    'long_description': 'Gradescope helps instructors grade exams and homework faster by grouping similar answers and applying rubrics automatically.',
                    'use_cases': 'Exam grading, Code grading, Homework',
                    'pros': 'Massive time saver, Consistent grading',
                    'cons': 'Setup overhead',
                    'pros_list': ['Batch grading', 'Rubric management', 'Integration'],
                    'cons_list': ['Scanning required', 'Learning curve']
                }
            },

            # --- Data Science ---
            {
                'name': 'Julius AI', 'slug': 'julius-ai',
                'website_url': 'https://julius.ai', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['data-scientist', 'student', 'marketer'],
                'categories': ['analytics', 'research'],
                'tags': ['data-viz', 'chatbot'],
                'translation': {
                    'short_description': 'Your AI data analyst.',
                    'long_description': 'Chat with your data. Upload Excel or CSV files and ask Julius to analyze trends, create charts, and perform advanced regression analysis.',
                    'use_cases': 'Data visualization, Statistical analysis, Cleaning data',
                    'pros': 'Very intuitive, Handles complex math',
                    'cons': 'File size limits',
                    'pros_list': ['Natural language', 'Good visualizations', 'Python export'],
                    'cons_list': ['Privacy for sensitive data', 'Limits']
                }
            },
            {
                'name': 'PandasAI', 'slug': 'pandas-ai',
                'website_url': 'https://getpandas.ai', 'pricing_type': 'free', 'is_featured': False,
                'professions': ['data-scientist', 'developer'],
                'categories': ['development', 'analytics'],
                'tags': ['code', 'data-viz', 'api'],
                'translation': {
                    'short_description': 'Generative AI capabilities for pandas dataframes.',
                    'long_description': 'A Python library that adds generative AI to pandas, allowing you to query your dataframes with natural language.',
                    'use_cases': 'Exploratory data analysis, Quick plotting',
                    'pros': 'Open source, Integrates with code',
                    'cons': 'Requires LLM API key',
                    'pros_list': ['Open source', 'Flexible', 'Developer friendly'],
                    'cons_list': ['LLM dependency', 'Accuracy check needed']
                }
            },

            # --- Video/Audio/Creative ---
            {
                'name': 'HeyGen', 'slug': 'heygen',
                'website_url': 'https://heygen.com', 'pricing_type': 'paid', 'is_featured': True,
                'professions': ['marketer', 'videographer', 'educator'],
                'categories': ['audio-video'],
                'tags': ['avatar', 'video', 'transcription'],
                'translation': {
                    'short_description': 'Create AI spokesman videos in minutes.',
                    'long_description': 'HeyGen allows you to generate professional business videos with customizable AI avatars and voice cloning. It also translates videos while lip-syncing.',
                    'use_cases': 'Marketing videos, Training content, Localization',
                    'pros': 'Incredible lip-sync, Video translation',
                    'cons': 'Pricey for high volume',
                    'pros_list': ['Lip-sync quality', 'Translation', 'Ease of use'],
                    'cons_list': ['Cost', 'Stock avatars recognizable']
                }
            },
            {
                'name': 'Suno', 'slug': 'suno',
                'website_url': 'https://suno.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['musician', 'content-creator'],
                'categories': ['audio-video'],
                'tags': ['music-generation'],
                'translation': {
                    'short_description': 'Make a song about anything.',
                    'long_description': 'Suno generates full songs with lyrics and vocals from a simple text prompt. The quality rivals professional production.',
                    'use_cases': 'Jingles, Content background, Fun',
                    'pros': 'Viral quality, Full vocals',
                    'cons': 'Copyright ambiguity',
                    'pros_list': ['Vocal generation', 'Style variety', 'Fast'],
                    'cons_list': ['Rights management', 'Inconsistent bitrate']
                }
            },
            
            # --- Productivity/General ---
            {
                'name': 'Rewind', 'slug': 'rewind',
                'website_url': 'https://rewind.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['entrepreneur', 'manager', 'developer'],
                'categories': ['productivity'],
                'tags': ['meeting-notes', 'automation'],
                'translation': {
                    'short_description': 'A personalized AI powered by everything you’ve seen, said, or heard.',
                    'long_description': 'Rewind records your screen and audio (locally) to let you search your past usage. "What did I look at last Tuesday about marketing?"',
                    'use_cases': 'Recall, Meeting logs, Personal productivity',
                    'pros': 'Local privacy, Perfect memory',
                    'cons': 'Mac only (mostly)',
                    'pros_list': ['Privacy first', 'Search everything', 'Lightweight'],
                    'cons_list': ['Platform limited', 'Storage usage']
                }
            },
            {
                'name': 'Mem', 'slug': 'mem',
                'website_url': 'https://mem.ai', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['writer', 'researcher'],
                'categories': ['productivity', 'knowledge-management'],
                'tags': ['automation', 'notes'],
                'translation': {
                    'short_description': 'The self-organizing workspace.',
                    'long_description': 'Mem is a note-taking app that uses AI to connect your notes automatically. It surfaces relevant information when you need it.',
                    'use_cases': 'Personal knowledge management, Journaling',
                    'pros': 'No folder structure needed, Smart search',
                    'cons': 'Different paradigm to learn',
                    'pros_list': ['Self-organizing', 'Chat with notes', 'Fast'],
                    'cons_list': ['Learning curve', 'Mobile app needs work']
                }
            },
            
            # --- Real Estate ---
            {
                'name': 'Restb.ai', 'slug': 'restb-ai',
                'website_url': 'https://restb.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['real-estate-agent'],
                'categories': ['analytics', 'design'],
                'tags': ['image-recognition', 'data-viz'],
                'translation': {
                    'short_description': 'Computer vision for real estate.',
                    'long_description': 'Restb.ai analyzes property photos to auto-tag features, detect room types, and even assess condition/renovation potential.',
                    'use_cases': 'Listing automation, Valuation, Search',
                    'pros': 'Automation for listings, Standardization',
                    'cons': 'Niche B2B focus',
                    'pros_list': ['Image tagging', 'Condition rating', 'Speed'],
                    'cons_list': ['B2B only', 'Integration complexity']
                }
            },

            # --- Game Dev ---
            {
                'name': 'Scenario', 'slug': 'scenario',
                'website_url': 'https://scenario.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['game-dev', 'designer'],
                'categories': ['design', 'development'],
                'tags': ['3d-modeling', 'image'],
                'translation': {
                    'short_description': 'AI-generated game assets.',
                    'long_description': 'Train AI models on your own art style to generate consistent game assets, textures, and sprites.',
                    'use_cases': 'Asset generation, Texturing, Concept art',
                    'pros': 'Style consistency, Speed',
                    'cons': '2D focus primarily',
                    'pros_list': ['Custom models', 'Consistency', 'Game ready'],
                    'cons_list': ['Complexity', 'Credits system']
                }
            },
            
            # --- Development ---
            {
                'name': 'Cursor', 'slug': 'cursor',
                'website_url': 'https://cursor.sh', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['developer'],
                'categories': ['development'],
                'tags': ['code', 'chatbot'],
                'translation': {
                    'short_description': 'The AI-first code editor.',
                    'long_description': 'A fork of VS Code with AI baked into the core. Chat with your codebase, debug errors automatically, and generate code diffs.',
                    'use_cases': 'Coding, Debugging, Refactoring',
                    'pros': 'Better than plugins, Chat with codebase',
                    'cons': 'Another IDE to install',
                    'pros_list': ['Codebase context', 'One-click fixes', 'VS Code compatible'],
                    'cons_list': ['Migration friction', 'Bugs occasionally']
                }
            },
            
            # --- Marketing ---
            {
                'name': 'BuzzSumo', 'slug': 'buzzsumo',
                'website_url': 'https://buzzsumo.com', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['marketer', 'writer'],
                'categories': ['marketing', 'analytics'],
                'tags': ['seo', 'research'],
                'translation': {
                    'short_description': 'Content research and monitoring tool.',
                    'long_description': 'Use AI to generate content ideas, monitor performance, and find influencers. Analyze what headlines are working across the web.',
                    'use_cases': 'Content strategy, Competitor analysis, PR',
                    'pros': 'Deep data, Trend spotting',
                    'cons': 'Interface feels dated',
                    'pros_list': ['Trend analysis', 'Influencer finding', 'Alerts'],
                    'cons_list': ['Cost', 'UI']
                }
            },

            # --- Finance ---
            {
                'name': 'Cleo', 'slug': 'cleo',
                'website_url': 'https://meetcleo.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['student', 'entrepreneur'],
                'categories': ['finance'],
                'tags': ['chatbot', 'data-viz'],
                'translation': {
                    'short_description': 'AI assistant for your personal finances.',
                    'long_description': 'Cleo roasts your spending habits to help you save. It categorizes transactions and provides a chat interface for your budget.',
                    'use_cases': 'Budgeting, Saving, Credit building',
                    'pros': 'Fun personality, engaging',
                    'cons': 'Access to bank data required',
                    'pros_list': ['Engagement', 'Simple budgeting', 'Personality'],
                    'cons_list': ['Bank connections', 'Roast mode intense']
                }
            },
        ]
        
        for data in tools_data:
            translation_data = data.pop('translation')
            
            # Extract lists
            pros_list = translation_data.pop('pros_list', [])
            cons_list = translation_data.pop('cons_list', [])
            
            profession_slugs = data.pop('professions', [])
            category_slugs = data.pop('categories', [])
            tag_slugs = data.pop('tags', [])
            
            tool, created = Tool.objects.update_or_create(slug=data['slug'], defaults={**data, 'status': 'published'})
            if created:
                self.stdout.write(f'  Created tool: {tool.name}')
            else:
                self.stdout.write(f'  Updated tool: {tool.name}')
            
            # Add relations (Handle loose matching safely)
            p_objs = [professions.get(s) for s in profession_slugs if professions.get(s)]
            if p_objs:
                tool.professions.add(*p_objs)
                
            c_objs = [categories.get(s) for s in category_slugs if categories.get(s)]
            if c_objs:
                tool.categories.add(*c_objs)
                
            t_objs = [tags.get(s) for s in tag_slugs if tags.get(s)]
            if t_objs:
                tool.tags.add(*t_objs)
            
            # Create translation with rich data
            # Map lists to newline separated strings if needed or store as text
            # Here we just keep the standard fields. 
            # Ideally model handles lists, but we fit into existing fields or append.
            
            if pros_list:
                translation_data['pros'] = "\n".join(pros_list)
            if cons_list:
                translation_data['cons'] = "\n".join(cons_list)
                
            ToolTranslation.objects.update_or_create(
                tool=tool, 
                language='en',
                defaults=translation_data
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {len(tools_data)} tools.'))
