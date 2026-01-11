from django.core.management.base import BaseCommand
from tools.models import Category, Profession, Tag, Tool, ToolTranslation, ToolStack


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create Professions
        professions_data = [
            {'name': 'Architect', 'slug': 'architect', 'icon': 'fa-solid fa-compass-drafting', 'hero_tagline': 'AI tools that help you design and plan faster'},
            {'name': 'Designer', 'slug': 'designer', 'icon': 'fa-solid fa-palette', 'hero_tagline': 'Creative AI tools for stunning visual work'},
            {'name': 'Marketer', 'slug': 'marketer', 'icon': 'fa-solid fa-bullhorn', 'hero_tagline': 'Automate campaigns and boost conversions'},
            {'name': 'Developer', 'slug': 'developer', 'icon': 'fa-solid fa-code', 'hero_tagline': 'Code faster with AI-powered assistance'},
            {'name': 'Writer', 'slug': 'writer', 'icon': 'fa-solid fa-pen-nib', 'hero_tagline': 'Write better content in less time'},
            {'name': 'Entrepreneur', 'slug': 'entrepreneur', 'icon': 'fa-solid fa-rocket', 'hero_tagline': 'AI tools to launch and scale your business'},
        ]
        
        professions = {}
        for data in professions_data:
            prof, _ = Profession.objects.update_or_create(slug=data['slug'], defaults=data)
            professions[data['slug']] = prof
            self.stdout.write(f'  Created profession: {prof.name}')
        
        # Create Categories
        categories_data = [
            {'name': 'Design', 'slug': 'design', 'icon': 'fa-solid fa-palette'},
            {'name': 'Automation', 'slug': 'automation', 'icon': 'fa-solid fa-robot'},
            {'name': 'Content', 'slug': 'content', 'icon': 'fa-solid fa-file-lines'},
            {'name': 'Analytics', 'slug': 'analytics', 'icon': 'fa-solid fa-chart-simple'},
            {'name': 'Development', 'slug': 'development', 'icon': 'fa-solid fa-code'},
            {'name': 'Audio/Video', 'slug': 'audio-video', 'icon': 'fa-solid fa-video'},
            {'name': 'Research', 'slug': 'research', 'icon': 'fa-solid fa-magnifying-glass'},
        ]
        
        categories = {}
        for data in categories_data:
            cat, _ = Category.objects.update_or_create(slug=data['slug'], defaults=data)
            categories[data['slug']] = cat
        
        # Create Tags
        tags_data = [
            'generative', 'automation', 'chatbot', 'image', 'video', 'text', 'code', 
            'analytics', 'free-tier', 'api', 'voice', 'transcription', 'presentation',
            '3d', 'UI-design', 'logo', 'marketing', 'seo', 'research'
        ]
        tags = {}
        for name in tags_data:
            tag, _ = Tag.objects.update_or_create(slug=name, defaults={'name': name.replace('-', ' ').title()})
            tags[name] = tag
        
        # Create Tools (Original 6 + 30 New = 36 Total)
        tools_data = [
            # Original 6
            {
                'name': 'ChatGPT', 'slug': 'chatgpt',
                'website_url': 'https://chat.openai.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['developer', 'writer', 'marketer', 'entrepreneur'], 'categories': ['content', 'automation'],
                'tags': ['chatbot', 'text', 'generative', 'free-tier'],
                'translation': {
                    'short_description': 'The most advanced AI assistant for writing, coding, and creative tasks.',
                    'long_description': 'ChatGPT is a state-of-the-art language model developed by OpenAI. It can help you write content, generate code, answer questions, and assist with a wide range of tasks.',
                    'use_cases': 'Content writing, Code generation, Research, Brainstorming',
                    'pros': 'Versatile, Free tier, Large knowledge base',
                    'cons': 'Can hallucinate, Training data cutoff'
                }
            },
            {
                'name': 'Midjourney', 'slug': 'midjourney',
                'website_url': 'https://midjourney.com', 'pricing_type': 'paid', 'is_featured': True,
                'professions': ['designer', 'architect', 'marketer'], 'categories': ['design'],
                'tags': ['image', 'generative'],
                'translation': {
                    'short_description': 'Create stunning AI-generated artwork and designs from text prompts.',
                    'long_description': 'Midjourney is a leading AI image generator known for its artistic style and high quality results. Perfect for concept art, architectural visualization, and creative projects.',
                    'use_cases': 'Concept art, Architectural viz, Marketing visuals',
                    'pros': 'High artistic quality, Active community',
                    'cons': 'Discord interface only, No free tier'
                }
            },
            {
                'name': 'GitHub Copilot', 'slug': 'github-copilot',
                'website_url': 'https://github.com/features/copilot', 'pricing_type': 'paid', 'is_featured': True,
                'professions': ['developer'], 'categories': ['development'],
                'tags': ['code', 'generative', 'automation'],
                'translation': {
                    'short_description': 'AI pair programmer that helping you write better code faster.',
                    'long_description': 'GitHub Copilot uses AI to suggest code completions and entire functions in real-time right from your editor.',
                    'use_cases': 'Code completion, Function generation, Test writing',
                    'pros': 'IDE integration, Productivity boost',
                    'cons': 'Subscription required, Privacy concerns'
                }
            },
            {
                'name': 'Jasper', 'slug': 'jasper',
                'website_url': 'https://jasper.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['marketer', 'writer'], 'categories': ['content'],
                'tags': ['text', 'generative', 'marketing'],
                'translation': {
                    'short_description': 'AI content platform for enterprise marketing teams.',
                    'long_description': 'Jasper is designed for marketing performance, helping teams check for brand voice and create on-brand content at scale.',
                    'use_cases': 'Blog posts, Ad copy, Social media',
                    'pros': 'Brand voice features, Templates',
                    'cons': 'Expensive, Learning curve'
                }
            },
            {
                'name': 'Canva AI', 'slug': 'canva-ai',
                'website_url': 'https://canva.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['designer', 'marketer', 'entrepreneur'], 'categories': ['design'],
                'tags': ['image', 'generative', 'free-tier'],
                'translation': {
                    'short_description': 'Design platform with built-in AI magic tools.',
                    'long_description': 'Canva integrates AI tools like Magic Design, Magic Edit, and Text to Image to make professional design accessible to everyone.',
                    'use_cases': 'Social graphics, Presentations, Logos',
                    'pros': 'User friendly, Free tier, All-in-one',
                    'cons': 'Limited advanced control'
                }
            },
            {
                'name': 'Notion AI', 'slug': 'notion-ai',
                'website_url': 'https://notion.so', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['entrepreneur', 'writer', 'marketer'], 'categories': ['content', 'automation'],
                'tags': ['text', 'automation'],
                'translation': {
                    'short_description': 'AI integrated directly into your workspace notes and docs.',
                    'long_description': 'Notion AI helps you write, summarize, and brainstorm without leaving your notes. It can extract action items and improve your writing.',
                    'use_cases': 'Summarization, Drafting, Editing',
                    'pros': 'Integrated workflow, Convenient',
                    'cons': 'Paid add-on'
                }
            },
            # NEW TOOLS (30)
            {
                'name': 'Claude 3', 'slug': 'claude-3',
                'website_url': 'https://anthropic.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['writer', 'developer', 'researcher'], 'categories': ['content', 'development'],
                'tags': ['chatbot', 'text', 'code', 'research'],
                'translation': {
                    'short_description': 'Advanced AI model with large context window for complex tasks.',
                    'long_description': 'Claude 3 Opus, Sonnet, and Haiku offer a balance of intelligence and speed. Known for handling large documents and coding tasks excellently.',
                    'use_cases': 'Long-form analysis, Coding, Creative writing',
                    'pros': 'Large context window, Natural writing style',
                    'cons': 'Daily limits on free tier'
                }
            },
            {
                'name': 'Stable Diffusion', 'slug': 'stable-diffusion',
                'website_url': 'https://stability.ai', 'pricing_type': 'free', 'is_featured': True,
                'professions': ['designer', 'architect'], 'categories': ['design'],
                'tags': ['image', 'generative', 'free-tier'],
                'translation': {
                    'short_description': 'Open-source text-to-image generation model.',
                    'long_description': 'Stable Diffusion offers incredible control and can be run locally. It is the foundation for many other AI art tools.',
                    'use_cases': 'Art generation, Texture creation, Inpainting',
                    'pros': 'Free/Open source, Local privacy',
                    'cons': 'Requires strong GPU for local run'
                }
            },
            {
                'name': 'Runway', 'slug': 'runway',
                'website_url': 'https://runwayml.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['designer', 'marketer'], 'categories': ['audio-video', 'design'],
                'tags': ['video', 'generative', 'image'],
                'translation': {
                    'short_description': 'AI video generation and editing suite.',
                    'long_description': 'Runway Gen-2 allows you to generate videos from text or images. It also offers advanced AI video editing tools.',
                    'use_cases': 'Video generation, Green screen, Inpainting',
                    'pros': 'Cutting edge video AI, Web-based',
                    'cons': 'Video generation is credit expensive'
                }
            },
            {
                'name': 'Otter.ai', 'slug': 'otter-ai',
                'website_url': 'https://otter.ai', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['entrepreneur', 'marketer'], 'categories': ['automation'],
                'tags': ['transcription', 'voice', 'automation'],
                'translation': {
                    'short_description': 'AI meeting assistant that records and transcribes audio.',
                    'long_description': 'Otter joins your meetings, records audio, writes notes, and captures slides automatically.',
                    'use_cases': 'Meeting notes, Interview transcription',
                    'pros': 'Real-time transcription, Speaker ID',
                    'cons': 'English focus primarily'
                }
            },
            {
                'name': 'Synthesia', 'slug': 'synthesia',
                'website_url': 'https://synthesia.io', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['marketer', 'entrepreneur'], 'categories': ['audio-video'],
                'tags': ['video', 'marketing', 'voice'],
                'translation': {
                    'short_description': 'Create AI videos with digital avatars.',
                    'long_description': 'Turn text into speech with a photorealistic AI avatar. ideal for training videos and marketing demos.',
                    'use_cases': 'Training videos, Explainers, Marketing',
                    'pros': 'No camera needed, Multilingual',
                    'cons': 'Can feel robotic occasionally'
                }
            },
            {
                'name': 'Copy.ai', 'slug': 'copy-ai',
                'website_url': 'https://copy.ai', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['marketer', 'writer'], 'categories': ['content'],
                'tags': ['text', 'marketing', 'generative'],
                'translation': {
                    'short_description': 'AI copywriting tool for marketing efficiency.',
                    'long_description': 'Generate high-converting copy for ads, emails, and websites in seconds.',
                    'use_cases': 'Ad copy, Email lines, Blog ideas',
                    'pros': 'Easy templates, Free plan available',
                    'cons': 'Generic outputs sometimes'
                }
            },
            {
                'name': 'ElevenLabs', 'slug': 'elevenlabs',
                'website_url': 'https://elevenlabs.io', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['developer', 'marketer'], 'categories': ['audio-video'],
                'tags': ['voice', 'generative', 'api'],
                'translation': {
                    'short_description': 'The most realistic AI voice generator.',
                    'long_description': 'Generate top-quality spoken audio in any voice, style, and language. Includes voice cloning capabilities.',
                    'use_cases': 'Audiobooks, Game chars, Video narration',
                    'pros': 'Incredible realism, Voice cloning',
                    'cons': 'Character limits on free tier'
                }
            },
            {
                'name': 'Perplexity', 'slug': 'perplexity',
                'website_url': 'https://perplexity.ai', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['researcher', 'writer', 'entrepreneur'], 'categories': ['research'],
                'tags': ['research', 'text', 'chatbot'],
                'translation': {
                    'short_description': 'AI search engine that provides cited answers.',
                    'long_description': 'Perplexity combines search with LLMs to give you precise answers with source citations.',
                    'use_cases': 'Market research, Fact checking, Learning',
                    'pros': 'Citations included, Up-to-date info',
                    'cons': 'Search dependent accuracy'
                }
            },
            {
                'name': 'Codeium', 'slug': 'codeium',
                'website_url': 'https://codeium.com', 'pricing_type': 'free', 'is_featured': False,
                'professions': ['developer'], 'categories': ['development'],
                'tags': ['code', 'free-tier', 'automation'],
                'translation': {
                    'short_description': 'Free AI code completion tool for developers.',
                    'long_description': 'A powerful alternative to Copilot that offers code completion and chat for free for individuals.',
                    'use_cases': 'Coding, Refactoring, Unit tests',
                    'pros': 'Free for individuals, Many IDEs supported',
                    'cons': 'Less integrated than Copilot in VS Code'
                }
            },
            {
                'name': 'Descript', 'slug': 'descript',
                'website_url': 'https://descript.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['marketer', 'writer'], 'categories': ['audio-video'],
                'tags': ['video', 'voice', 'automation'],
                'translation': {
                    'short_description': 'Edit video and audio by editing text.',
                    'long_description': 'Descript transcribes your media and lets you edit the text to cut the video. Includes "Studio Sound" AI enhancement.',
                    'use_cases': 'Podcast editing, Video clips, Screen recording',
                    'pros': 'Innovative workflow, Overdub feature',
                    'cons': 'Resource heavy app'
                }
            },
            {
                'name': 'Llama 3', 'slug': 'llama-3',
                'website_url': 'https://llama.meta.com', 'pricing_type': 'free', 'is_featured': False,
                'professions': ['developer', 'researcher'], 'categories': ['development'],
                'tags': ['code', 'text', 'free-tier'],
                'translation': {
                    'short_description': 'State-of-the-art open source LLM from Meta.',
                    'long_description': 'Llama 3 allows developers to build and run their own AI applications locally or in the cloud without API dependencies.',
                    'use_cases': 'Local chatbots, Private data analysis',
                    'pros': 'Open weights, High performance',
                    'cons': 'Requires technical setup'
                }
            },
            {
                'name': 'Looka', 'slug': 'looka',
                'website_url': 'https://looka.com', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['entrepreneur', 'designer'], 'categories': ['design'],
                'tags': ['logo', 'design', 'generative'],
                'translation': {
                    'short_description': 'Design your own beautiful brand and logo with AI.',
                    'long_description': 'Looka generates logo options based on your preferences and builds a whole brand kit around them.',
                    'use_cases': 'Logo design, Brand kits, Business cards',
                    'pros': 'Quick branding, Professional assets',
                    'cons': 'SVG download is paid'
                }
            },
            {
                'name': 'Uizard', 'slug': 'uizard',
                'website_url': 'https://uizard.io', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['designer', 'entrepreneur'], 'categories': ['design'],
                'tags': ['UI-design', 'generative'],
                'translation': {
                    'short_description': 'Design wireframes, mockups, and prototypes in minutes.',
                    'long_description': 'Scan hand-drawn sketches to turn them into editable app designs automatically.',
                    'use_cases': 'App prototyping, Wireframing, UI design',
                    'pros': 'Sketch to screen, Easy to use',
                    'cons': 'Limited complex interactions'
                }
            },
            {
                'name': 'Beautiful.ai', 'slug': 'beautiful-ai',
                'website_url': 'https://beautiful.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['entrepreneur', 'marketer'], 'categories': ['design'],
                'tags': ['presentation', 'generative'],
                'translation': {
                    'short_description': 'Generative AI presentation software for workplace.',
                    'long_description': 'Smart slide templates that adapt automatically as you add content, keeping everything professionally designed.',
                    'use_cases': 'Pitch decks, Reports, Sales slides',
                    'pros': 'Always looks good, Time saving',
                    'cons': 'Subscription only'
                }
            },
            {
                'name': 'Gamma', 'slug': 'gamma',
                'website_url': 'https://gamma.app', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['entrepreneur', 'marketer'], 'categories': ['design', 'content'],
                'tags': ['presentation', 'generative', 'text'],
                'translation': {
                    'short_description': 'Generate presentations, docs, and webpages in seconds.',
                    'long_description': 'Gamma uses AI to generate entire slide decks or documents from a simple prompt.',
                    'use_cases': 'Decks, Memos, Briefs',
                    'pros': 'Very fast generation, Modern look',
                    'cons': 'Limited layout customization'
                }
            },
            {
                'name': 'Zapier', 'slug': 'zapier',
                'website_url': 'https://zapier.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['entrepreneur', 'marketer', 'automation-specialist'], 'categories': ['automation'],
                'tags': ['automation', 'text', 'api'],
                'translation': {
                    'short_description': 'Automate your workflow by connecting apps.',
                    'long_description': 'Zapier now includes AI features to build workflows with natural language and connect AI models to thousands of apps.',
                    'use_cases': 'Workflow automation, Data syncing',
                    'pros': 'Huge app ecosystem',
                    'cons': 'Complex zaps get expensive'
                }
            },
            {
                'name': 'GrammarlyGO', 'slug': 'grammarly-go',
                'website_url': 'https://grammarly.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['writer', 'entrepreneur'], 'categories': ['content'],
                'tags': ['text', 'automation'],
                'translation': {
                    'short_description': 'AI writing assistance that works everywhere you write.',
                    'long_description': 'Grammarly goes beyond spelling to check tone, clarity, and now generates text with AI context awareness.',
                    'use_cases': 'Proofreading, Email rewriting, Tone check',
                    'pros': 'Browser extension, High accuracy',
                    'cons': 'Premium features expensive'
                }
            },
            {
                'name': 'Fireflies.ai', 'slug': 'fireflies-ai',
                'website_url': 'https://fireflies.ai', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['manager', 'entrepreneur'], 'categories': ['automation'],
                'tags': ['voice', 'transcription', 'automation'],
                'translation': {
                    'short_description': 'Automate your meeting notes.',
                    'long_description': 'Fireflies records, transcribes, searches, and analyzes voice conversations.',
                    'use_cases': 'Meeting minutes, Team syncs',
                    'pros': 'Integrates with CRM, Good search',
                    'cons': 'Accuracy varies by accent'
                }
            },
            {
                'name': 'Murf.ai', 'slug': 'murf-ai',
                'website_url': 'https://murf.ai', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['marketer', 'content-creator'], 'categories': ['audio-video'],
                'tags': ['voice', 'generative'],
                'translation': {
                    'short_description': 'Go from text to speech with a versatile AI voice generator.',
                    'long_description': 'Murf enables you to create studio-quality voiceovers in minutes. Great for podcasts, videos, and professional presentations.',
                    'use_cases': 'E-learning, Youtube videos, IVR',
                    'pros': 'Control over pitch/speed, Media sync',
                    'cons': 'Download limits on free plan'
                }
            },
            {
                'name': 'Framer AI', 'slug': 'framer-ai',
                'website_url': 'https://framer.com', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['designer', 'developer'], 'categories': ['design', 'development'],
                'tags': ['UI-design', 'code', 'generative'],
                'translation': {
                    'short_description': 'Generate and publish your dream site with AI.',
                    'long_description': 'Framer lets you design and publish websites. Its AI features generate layouts and copy to get you started instantly.',
                    'use_cases': 'Portfolio sites, Landing pages',
                    'pros': 'High quality design, No code publish',
                    'cons': 'Learning curve for advanced interaction'
                }
            },
            {
                'name': '10Web', 'slug': '10web',
                'website_url': 'https://10web.io', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['entrepreneur', 'developer'], 'categories': ['development'],
                'tags': ['code', 'automation', 'website'],
                'translation': {
                    'short_description': 'AI-powered WordPress platform builder.',
                    'long_description': 'Build or recreate any website with AI in minutes on top of WordPress.',
                    'use_cases': 'Business websites, WP hosting',
                    'pros': 'Recreate existing sites, WP ecosystem',
                    'cons': 'Platform lock-in for hosting'
                }
            },
            {
                'name': 'Writesonic', 'slug': 'writesonic',
                'website_url': 'https://writesonic.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['writer', 'marketer'], 'categories': ['content'],
                'tags': ['text', 'seo', 'generative'],
                'translation': {
                    'short_description': 'SEO-optimized content creation.',
                    'long_description': 'Writesonic focuses on creating SEO-friendly content for blogs, Facebook ads, Google ads, and Shopify.',
                    'use_cases': 'SEO Articles, Product descriptions',
                    'pros': 'SEO integration, Article writer 5.0',
                    'cons': 'Credit based system'
                }
            },
            {
                'name': 'QuillBot', 'slug': 'quillbot',
                'website_url': 'https://quillbot.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['writer', 'student'], 'categories': ['content'],
                'tags': ['text', 'automation'],
                'translation': {
                    'short_description': 'AI-powered paraphrasing tool.',
                    'long_description': 'QuillBot helps you rewrite text to improve clarity, vocabulary, and tone.',
                    'use_cases': 'Rewriting, Plagiarism check, Grammar',
                    'pros': 'Excellent paraphrasing, Free mode',
                    'cons': 'Word limit on free version'
                }
            },
            {
                'name': 'Pictory', 'slug': 'pictory',
                'website_url': 'https://pictory.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['marketer', 'content-creator'], 'categories': ['audio-video'],
                'tags': ['video', 'automation', 'text'],
                'translation': {
                    'short_description': 'Automatically create short, highly shareable branded videos from long form content.',
                    'long_description': 'Turn scripts or blog posts into videos, or extract snippets from Zoom recordings automatically.',
                    'use_cases': 'Social clips, Blog to video',
                    'pros': 'Great for repurposing content',
                    'cons': 'Stock footage can feel generic'
                }
            },
            {
                'name': 'AdCreative.ai', 'slug': 'adcreative-ai',
                'website_url': 'https://adcreative.ai', 'pricing_type': 'paid', 'is_featured': False,
                'professions': ['marketer', 'entrepreneur'], 'categories': ['design', 'analytics'],
                'tags': ['marketing', 'design', 'analytics'],
                'translation': {
                    'short_description': 'Generate conversion-focused ad creatives and banners.',
                    'long_description': 'AI that generates ad creatives based on data-driven insights to maximize conversion rates.',
                    'use_cases': 'Display ads, Social media ads',
                    'pros': 'Performance focused, Scalable',
                    'cons': 'Design flexibility limited'
                }
            },
            {
                'name': 'Hugging Face', 'slug': 'hugging-face',
                'website_url': 'https://huggingface.co', 'pricing_type': 'free', 'is_featured': True,
                'professions': ['developer', 'researcher'], 'categories': ['development', 'research'],
                'tags': ['code', 'api', 'free-tier'],
                'translation': {
                    'short_description': 'The AI community building the future.',
                    'long_description': 'The hub for open source models, datasets, and demo apps. Essential for any AI developer.',
                    'use_cases': 'Model hosting, Dataset search',
                    'pros': 'Standard for open source, Huge library',
                    'cons': 'Technical interface'
                }
            },
            {
                'name': 'LangChain', 'slug': 'langchain',
                'website_url': 'https://langchain.com', 'pricing_type': 'free', 'is_featured': False,
                'professions': ['developer'], 'categories': ['development'],
                'tags': ['code', 'api'],
                'translation': {
                    'short_description': 'Framework for developing applications powered by language models.',
                    'long_description': 'LangChain makes it easy to connect LLMs to other sources of data and allow them to interact with their environment.',
                    'use_cases': 'Building chatbots, RAG apps',
                    'pros': 'Standard framework, Flexible',
                    'cons': 'Rapidly changing API'
                }
            },
            {
                'name': 'Tabnine', 'slug': 'tabnine',
                'website_url': 'https://tabnine.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['developer'], 'categories': ['development'],
                'tags': ['code', 'automation'],
                'translation': {
                    'short_description': 'AI assistant for software developers.',
                    'long_description': 'Tabnine predicts and suggests your next lines of code based on context & syntax.',
                    'use_cases': 'Code completion, Privacy-first coding',
                    'pros': 'Private code models, Fast',
                    'cons': 'Less "chatty" than Copilot'
                }
            },
            {
                'name': 'Liner', 'slug': 'liner',
                'website_url': 'https://getliner.com', 'pricing_type': 'freemium', 'is_featured': False,
                'professions': ['researcher', 'student'], 'categories': ['research'],
                'tags': ['text', 'research'],
                'translation': {
                    'short_description': 'AI Workspace for efficient research.',
                    'long_description': 'Highlight text anywhere on the web, manage insights, and ask AI to summarize.',
                    'use_cases': 'Web highlighting, Research organization',
                    'pros': 'Great browser extension',
                    'cons': 'Subscription for advanced AI'
                }
            },
            {
                'name': 'Tome', 'slug': 'tome',
                'website_url': 'https://tome.app', 'pricing_type': 'freemium', 'is_featured': True,
                'professions': ['entrepreneur', 'marketer'], 'categories': ['design', 'content'],
                'tags': ['presentation', 'generative', 'storytelling'],
                'translation': {
                    'short_description': 'AI-powered storytelling format.',
                    'long_description': 'Tome creates polished, interactive narratives and presentations from your prompts.',
                    'use_cases': 'Pitch decks, Visual stories',
                    'pros': 'Interactive format, Mobile friendly',
                    'cons': 'Not a traditional slide export'
                }
            }
        ]
        
        created_tools = []
        for data in tools_data:
            translation_data = data.pop('translation')
            profession_slugs = data.pop('professions', [])
            category_slugs = data.pop('categories', [])
            tag_slugs = data.pop('tags', [])
            
            tool, _ = Tool.objects.update_or_create(slug=data['slug'], defaults={**data, 'status': 'published'})
            
            # Add relations (handle missing keys safely if any)
            if profession_slugs:
                tool.professions.set([professions.get(s) for s in profession_slugs if professions.get(s)])
            
            if category_slugs:
                tool.categories.set([categories.get(s) for s in category_slugs if categories.get(s)])
                
            if tag_slugs:
                tool.tags.set([tags.get(s) for s in tag_slugs if tags.get(s)])
            
            # Create translation
            ToolTranslation.objects.update_or_create(
                tool=tool, 
                language='en',
                defaults=translation_data
            )
            
            created_tools.append(tool)
            self.stdout.write(f'  Created tool: {tool.name}')
        
        # Create Tool Stacks
        stacks_data = [
            {
                'name': 'Content Creator Toolkit',
                'slug': 'content-creator-toolkit',
                'tagline': 'Everything you need to create engaging content',
                'description': 'This stack combines the best AI tools for content creators. From writing and editing to visual design, these tools work together to help you produce high-quality content efficiently.',
                'workflow_description': '1. Use ChatGPT to brainstorm and draft content\n2. Refine with Jasper for marketing copy\n3. Create visuals with Canva AI\n4. Organize everything in Notion',
                'is_featured': True,
                'tools': ['chatgpt', 'jasper', 'canva-ai', 'notion-ai'],
                'professions': ['marketer', 'writer'],
            },
            {
                'name': 'Developer Power Pack',
                'slug': 'developer-power-pack',
                'tagline': 'Write better code faster with AI assistance',
                'description': 'Essential AI tools for modern software development. From code generation to documentation, this stack helps developers be more productive and write cleaner code.',
                'workflow_description': '1. Use GitHub Copilot for code completion\n2. Ask ChatGPT or Claude 3 for complex problem solving\n3. Document your work with Notion AI',
                'is_featured': True,
                'tools': ['github-copilot', 'chatgpt', 'notion-ai', 'claude-3', 'codeium'],
                'professions': ['developer'],
            },
            {
                'name': 'Design & Visualization Stack',
                'slug': 'design-visualization-stack',
                'tagline': 'AI-powered design for architects and designers',
                'description': 'Perfect for visual professionals who need to create stunning imagery quickly. From concept art to final presentations.',
                'workflow_description': '1. Generate concepts with Midjourney or Stable Diffusion\n2. Polish and adapt with Canva AI\n3. Present and collaborate via Notion',
                'is_featured': True,
                'tools': ['midjourney', 'canva-ai', 'notion-ai', 'stable-diffusion'],
                'professions': ['designer', 'architect'],
            },
            {
                'name': 'Startup Launchpad',
                'slug': 'startup-launchpad',
                'tagline': 'Launch your business in record time',
                'description': 'A complete suite of tools to name, brand, build, and market your new startup.',
                'workflow_description': '1. Brainstorm with ChatGPT\n2. Create logo with Looka\n3. Build site with Framer AI or 10Web\n4. Create content with Copy.ai',
                'is_featured': True,
                'tools': ['chatgpt', 'looka', 'framer-ai', 'copy-ai', 'beautiful-ai'],
                'professions': ['entrepreneur'],
            },
        ]
        
        for data in stacks_data:
            tool_slugs = data.pop('tools')
            profession_slugs = data.pop('professions')
            
            stack, _ = ToolStack.objects.update_or_create(slug=data['slug'], defaults=data)
            stack.tools.set(Tool.objects.filter(slug__in=tool_slugs))
            stack.professions.set([professions[s] for s in profession_slugs if professions.get(s)])
            self.stdout.write(f'  Created stack: {stack.name}')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
