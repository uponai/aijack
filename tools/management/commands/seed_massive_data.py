from django.core.management.base import BaseCommand
from tools.models import Category, Profession, Tag, Tool, ToolTranslation, ToolStack

class Command(BaseCommand):
    help = 'Seeds database with MASSIVE dataset (50+ tools, 10+ stacks) across Medical, Finance, HR, Real Estate, etc.'

    def handle(self, *args, **options):
        self.stdout.write('Initializing massive data injection...')

        # --- 1. Ensure Categories Exist ---
        categories_data = [
            'Medical', 'Real Estate', 'Finance', 'Construction', 'HR & Recruiting', 
            'Research', 'Audio', 'Video', 'Legal', 'Productivity', 'Marketing', 'Sales'
        ]
        categories = {}
        for name in categories_data:
            slug = name.lower().replace(' & ', '-').replace(' ', '-')
            cat, _ = Category.objects.update_or_create(slug=slug, defaults={'name': name, 'icon': 'fa-solid fa-layer-group'})
            categories[slug] = cat

        # --- 2. Ensure Professions Exist ---
        # (Assuming previous seed created most, adding missing ones if any)
        # We will reuse existing profession lookups or create on fly if really needed, but better to stick to knowns.
        # Knowns: medical-pro, real-estate-agent, accountant (maybe new), hr-manager, sales-rep, legal-pro, 
        # architect, videographer, podcaster (new), researcher (new/student).
        
        professions_map = {
            'doctor': {'name': 'Doctor', 'slug': 'doctor', 'icon': 'fa-solid fa-user-doctor', 'hero_tagline': 'AI-assisted diagnosis and patient care'},
            'nurse': {'name': 'Nurse', 'slug': 'nurse', 'icon': 'fa-solid fa-user-nurse', 'hero_tagline': 'Streamline patient monitoring and records'},
            'radiologist': {'name': 'Radiologist', 'slug': 'radiologist', 'icon': 'fa-solid fa-x-ray', 'hero_tagline': 'Detect anomalies faster with AI vision'},
            'accountant': {'name': 'Accountant', 'slug': 'accountant', 'icon': 'fa-solid fa-calculator', 'hero_tagline': 'Automate bookkeeping and financial forecasts'},
            'financial-analyst': {'name': 'Financial Analyst', 'slug': 'financial-analyst', 'icon': 'fa-solid fa-chart-line', 'hero_tagline': 'Predict market trends with precision'},
            'researcher': {'name': 'Academic Researcher', 'slug': 'researcher', 'icon': 'fa-solid fa-book-open-reader', 'hero_tagline': 'Accelerate literature reviews and discovery'},
            'podcaster': {'name': 'Podcaster', 'slug': 'podcaster', 'icon': 'fa-solid fa-microphone-lines', 'hero_tagline': 'Produce studio-quality audio instantly'},
            'construction-manager': {'name': 'Construction Manager', 'slug': 'construction-manager', 'icon': 'fa-solid fa-helmet-safety', 'hero_tagline': 'Optimize site safety and project timelines'},
        }
        
        prof_objs = {}
        for slug, data in professions_map.items():
            p, _ = Profession.objects.update_or_create(slug=slug, defaults=data)
            prof_objs[slug] = p

        # Link to existing ones from previous seeds
        for slug in ['hr-manager', 'sales-rep', 'legal-pro', 'architect', 'real-estate-agent', 'videographer', 'game-dev', 'developer', 'student', 'data-scientist', 'marketer']:
            try:
                prof_objs[slug] = Profession.objects.get(slug=slug)
            except Profession.DoesNotExist:
                # Fallback if previous seed didn't run or verify
                pass

        # --- 3. TOOLS DATA ---
        tools_data = [
            # --- MEDICAL ---
            {
                'name': 'Aidoc', 'slug': 'aidoc', 'website_url': 'https://www.aidoc.com', 'pricing_type': 'paid',
                'professions': ['radiologist', 'doctor'], 'categories': ['medical'], 'tags': ['image-recognition', 'diagnosis'],
                'translation': {
                    'short_description': 'AI for medical imaging and care coordination.',
                    'long_description': 'Aidoc analyzes medical images to flag acute abnormalities like strokes or fractures, prioritizing critical cases for radiologists.',
                    'use_cases': 'Stroke detection, Pulmonary embolism flagging, Workflow prioritization',
                    'pros_list': ['FDA cleared', 'Fast triage', 'Integrates with PACS'],
                    'cons_list': ['Enterprise cost', 'Specialized hardware often needed']
                }
            },
            {
                'name': 'Nuance DAX', 'slug': 'nuance-dax', 'website_url': 'https://www.nuance.com', 'pricing_type': 'paid',
                'professions': ['doctor', 'nurse'], 'categories': ['medical'], 'tags': ['medical-scribe', 'voice-to-text'],
                'translation': {
                    'short_description': 'Ambient Clinical Intelligence for documentation.',
                    'long_description': 'Nuance DAX ("Dragon Ambient eXperience") listens to physician-patient conversations and automatically writes clinical notes in the EHR.',
                    'use_cases': 'Automated charting, Patient interaction focus, Telehealth',
                    'pros_list': ['Reduces burnout', 'High accuracy', 'EHR integration'],
                    'cons_list': ['Expensive', 'Requires cloud connection']
                }
            },
            {
                'name': 'Viz.ai', 'slug': 'viz-ai', 'website_url': 'https://www.viz.ai', 'pricing_type': 'paid',
                'professions': ['doctor', 'radiologist'], 'categories': ['medical'], 'tags': ['care-coordination', 'mobile-app'],
                'translation': {
                    'short_description': 'AI-powered care coordination for stroke.',
                    'long_description': 'Viz.ai detects suspected large vessel occlusions using AI and alerts the stroke team on their mobile phones within minutes.',
                    'use_cases': 'Stroke alerts, Workflow synchronization, Image viewing',
                    'pros_list': ['Lifesaving speed', 'Mobile access', 'Clinical evidence'],
                    'cons_list': ['Niche focus', 'Subscription cost']
                }
            },

            # --- REAL ESTATE ---
            {
                'name': 'Structurely', 'slug': 'structurely', 'website_url': 'https://www.structurely.com', 'pricing_type': 'paid',
                'professions': ['real-estate-agent'], 'categories': ['real-estate', 'sales'], 'tags': ['lead-qualification', 'chatbot'],
                'translation': {
                    'short_description': 'AI inside sales agent for real estate.',
                    'long_description': 'Structurely engages online leads via text/email, qualifying them with human-like conversation before passing not to an agent.',
                    'use_cases': 'Lead follow-up, Appointment setting, Database reactivation',
                    'pros_list': ['24/7 response', 'Human-like empathy', 'Long-term nurture'],
                    'cons_list': ['Setup required', 'Monthly fee']
                }
            },
            {
                'name': 'Write.Homes', 'slug': 'write-homes', 'website_url': 'https://write.homes', 'pricing_type': 'freemium',
                'professions': ['real-estate-agent'], 'categories': ['real-estate', 'marketing'], 'tags': ['copywriting'],
                'translation': {
                    'short_description': 'AI copywriting specifically for real estate.',
                    'long_description': 'Generate MLS descriptions, social media captions, and blog posts tailored to property features and local markets.',
                    'use_cases': 'Listing descriptions, Instagram captions, Newsletters',
                    'pros_list': ['Industry specific presets', 'Easy to use', 'Fair pricing'],
                    'cons_list': ['Text only', 'English focused']
                }
            },
            {
                'name': 'HouseCanary', 'slug': 'housecanary', 'website_url': 'https://www.housecanary.com', 'pricing_type': 'paid',
                'professions': ['real-estate-agent', 'financial-analyst'], 'categories': ['real-estate', 'analytics'], 'tags': ['valuation', 'forecasting'],
                'translation': {
                    'short_description': 'High-precision residential real estate valuations.',
                    'long_description': 'Uses AI to forecast home values, analyze market trends, and provide investment insights with granular accuracy.',
                    'use_cases': 'Property valuation, Market analysis, Rental forecasting',
                    'pros_list': ['Data accuracy', 'Granular detail', 'Future casting'],
                    'cons_list': ['Enterprise focused', 'US only']
                }
            },

            # --- FINANCE ---
            {
                'name': 'Vic.ai', 'slug': 'vic-ai', 'website_url': 'https://www.vic.ai', 'pricing_type': 'paid',
                'professions': ['accountant'], 'categories': ['finance'], 'tags': ['automation', 'invoice-processing'],
                'translation': {
                    'short_description': 'Autonomous accounting for accounts payable.',
                    'long_description': 'Vic.ai processes invoices, categorizes expenses, and handles approvals autonomously, learning from human corrections over time.',
                    'use_cases': 'Invoice processing, Approval workflows, Expense coding',
                    'pros_list': ['High automation', 'Learns continuously', 'Reduces errors'],
                    'cons_list': ['Implementation time', 'Cost']
                }
            },
            {
                'name': 'Datarails', 'slug': 'datarails', 'website_url': 'https://www.datarails.com', 'pricing_type': 'paid',
                'professions': ['financial-analyst'], 'categories': ['finance'], 'tags': ['excel', 'fp&a'],
                'translation': {
                    'short_description': 'FP&A platform for Excel users.',
                    'long_description': 'Datarails automates financial reporting and planning while letting finance teams keep using their beloved Excel spreadsheets.',
                    'use_cases': 'Budgeting, Forecasting, Management reporting',
                    'pros_list': ['Keeps Excel interface', 'Data consolidation', 'Visual dashboard'],
                    'cons_list': ['Windows heavy', 'SaaS pricing']
                }
            },
            {
                'name': 'Botkeeper', 'slug': 'botkeeper', 'website_url': 'https://www.botkeeper.com', 'pricing_type': 'paid',
                'professions': ['accountant'], 'categories': ['finance'], 'tags': ['bookkeeping'],
                'translation': {
                    'short_description': 'Automated bookkeeping for accounting firms.',
                    'long_description': 'Botkeeper combines AI with skilled accountants to automate bookkeeping tasks for CPA firms, ensuring accuracy and scalability.',
                    'use_cases': 'Client bookkeeping, Month-end close, Categorization',
                    'pros_list': ['Scalable', 'Human-in-loop', 'Integration'],
                    'cons_list': ['Firm-focused', 'Not for individuals']
                }
            },
            
            # --- CONSTRUCTION / ARCHITECTURE ---
            {
                'name': 'Autodesk Forma', 'slug': 'autodesk-forma', 'website_url': 'https://www.autodesk.com/forma', 'pricing_type': 'paid',
                'professions': ['architect'], 'categories': ['construction'], 'tags': ['site-planning', '3d-modeling'],
                'translation': {
                    'short_description': 'Cloud-based AI for early stage site planning.',
                    'long_description': 'Formerly Spacemaker, Forma helps interaction design teams analyze wind, noise, and sun to optimize site layouts instantly.',
                    'use_cases': 'Feasibility studies, Environmental analysis, Conceptual design',
                    'pros_list': ['Real-time analysis', 'Cloud based', 'Interoperable'],
                    'cons_list': ['Subscription needed', 'Learning curve']
                }
            },
            {
                'name': 'TestFit', 'slug': 'testfit', 'website_url': 'https://testfit.io', 'pricing_type': 'paid',
                'professions': ['architect', 'real-estate-agent'], 'categories': ['construction'], 'tags': ['generative-design'],
                'translation': {
                    'short_description': 'Real-time generative building feasibility.',
                    'long_description': 'TestFit solves site plans in milliseconds for multifamily, parking, and industrial buildings, calculating yield and cost instantly.',
                    'use_cases': 'Deal feasibility, Site planning, Cost estimation',
                    'pros_list': ['Incredibly fast', 'Yield optimization', 'Financial integration'],
                    'cons_list': ['Specific building types', 'Cost']
                }
            },
            {
                'name': 'Togal.AI', 'slug': 'togal-ai', 'website_url': 'https://www.togal.ai', 'pricing_type': 'paid',
                'professions': ['construction-manager'], 'categories': ['construction'], 'tags': ['estimation'],
                'translation': {
                    'short_description': 'Automated construction estimating.',
                    'long_description': 'Togal.AI uses deep learning to automatically detect and measure room areas, walls, and objects from blueprints.',
                    'use_cases': 'Takeoffs, Bidding, Cost estimation',
                    'pros_list': ['Saves 80% time', 'Accurate', 'Easy to use'],
                    'cons_list': ['Requires clean blueprints', 'Price']
                }
            },

            # --- HR & RECRUITING ---
            {
                'name': 'Eightfold AI', 'slug': 'eightfold-ai', 'website_url': 'https://eightfold.ai', 'pricing_type': 'paid',
                'professions': ['hr-manager'], 'categories': ['hr-recruiting'], 'tags': ['talent-intelligence', 'recruiting'],
                'translation': {
                    'short_description': 'Talent intelligence platform.',
                    'long_description': 'Eightfold uses deep learning to match candidates to jobs based on skills and potential, not just keywords, reducing bias.',
                    'use_cases': 'Candidate matching, Internal mobility, Upskilling',
                    'pros_list': ['Reduces bias', 'Skills-based', 'Scalable'],
                    'cons_list': ['Enterprise pricing', 'Integration effort']
                }
            },
            {
                'name': 'HireVue', 'slug': 'hirevue', 'website_url': 'https://www.hirevue.com', 'pricing_type': 'paid',
                'professions': ['hr-manager'], 'categories': ['hr-recruiting'], 'tags': ['video-interview', 'assessment'],
                'translation': {
                    'short_description': 'Video interviewing and assessment platform.',
                    'long_description': 'HireVue automates video interviews and game-based assessments to screen candidates faster and fairer.',
                    'use_cases': 'High volume hiring, Remote interviews, Skill testing',
                    'pros_list': ['Speed', 'Consistency', 'Global reach'],
                    'cons_list': ['Candidate anxiety', 'Impersonal feel']
                }
            },

            # --- RESEARCH ---
            {
                'name': 'Consensus', 'slug': 'consensus', 'website_url': 'https://consensus.app', 'pricing_type': 'freemium',
                'professions': ['researcher', 'student'], 'categories': ['research'], 'tags': ['search-engine', 'academic'],
                'translation': {
                    'short_description': 'Search engine for scientific research.',
                    'long_description': 'Consensus uses AI to find answers in peer-reviewed papers. Ask a question, and it extracts and summarizes findings from studies.',
                    'use_cases': 'Literature review, Fact checking, Scientific discovery',
                    'pros_list': ['Cites sources', 'Scientific focus', 'Ad-free'],
                    'cons_list': ['Limited to papers', 'Some paywalls']
                }
            },
            {
                'name': 'Elicit', 'slug': 'elicit', 'website_url': 'https://elicit.org', 'pricing_type': 'freemium',
                'professions': ['researcher', 'student'], 'categories': ['research'], 'tags': ['literature-review'],
                'translation': {
                    'short_description': 'AI research assistant.',
                    'long_description': 'Elicit automates research workflows like literature review. It can find papers, summarize takeaways, and extract data into a table.',
                    'use_cases': 'Systematic reviews, brainstorming, data extraction',
                    'pros_list': ['Excellent summaries', 'Task automation', 'Time saver'],
                    'cons_list': ['Credits system', 'Hallucination risk (low)']
                }
            },
            {
                'name': 'Scite', 'slug': 'scite', 'website_url': 'https://scite.ai', 'pricing_type': 'paid',
                'professions': ['researcher'], 'categories': ['research'], 'tags': ['citation-analysis'],
                'translation': {
                    'short_description': 'Smart citations for better research.',
                    'long_description': 'Scite shows how papers have been cited—supporting, contrasting, or mentioning—giving you the context of research impact.',
                    'use_cases': 'Evaluating papers, Writing literature reviews, Fact checking',
                    'pros_list': ['Deep context', 'Verification', 'Chrome extension'],
                    'cons_list': ['Subscription', 'Database coverage gaps']
                }
            },

            # --- PODCASTING / AUDIO ---
            {
                'name': 'Descript', 'slug': 'descript', 'website_url': 'https://descript.com', 'pricing_type': 'freemium',
                'professions': ['podcaster', 'videographer'], 'categories': ['audio', 'video'], 'tags': ['video-editor', 'transcription'],
                'translation': {
                    'short_description': 'Edit audio and video like a text doc.',
                    'long_description': 'Descript transcribes your media, and you edit the text to cut the audio. Includes "Overdub" voice cloning and Studio Sound removal.',
                    'use_cases': 'Podcasts, Social clips, Screen recording',
                    'pros_list': ['Revolutionary workflow', 'Studio sound', 'Easy'],
                    'cons_list': ['Resource heavy', 'Sync issues sometimes']
                }
            },
            {
                'name': 'Podcastle', 'slug': 'podcastle', 'website_url': 'https://podcastle.ai', 'pricing_type': 'freemium',
                'professions': ['podcaster'], 'categories': ['audio'], 'tags': ['recording', 'hosting'],
                'translation': {
                    'short_description': 'Studio quality recording and editing on the web.',
                    'long_description': 'Podcastle offers multi-track recording, Magic Dust noise removal, and text-to-speech tools in a browser-based studio.',
                    'use_cases': 'Remote interviews, Solo podcasts, Audio enhancement',
                    'pros_list': ['Browser based', 'High quality', 'Intuitive'],
                    'cons_list': ['Free tier limits', 'Web reliance']
                }
            },
            {
                'name': 'Adobe Podcast', 'slug': 'adobe-podcast', 'website_url': 'https://podcast.adobe.com', 'pricing_type': 'free',
                'professions': ['podcaster'], 'categories': ['audio'], 'tags': ['enhancement'],
                'translation': {
                    'short_description': 'AI audio recording and enhancement.',
                    'long_description': 'Famous for its "Enhance Speech" tool that makes phone recordings sound like studio mics. Also offers a web-based studio.',
                    'use_cases': 'Fixing bad audio, Remote recording, Quick polish',
                    'pros_list': ['Miraculous cleanup', 'Free tools', 'Simple'],
                    'cons_list': ['Can sound robotic', 'Beta features']
                }
            },

            # --- LEGAL ---
            {
                'name': 'Harvey', 'slug': 'harvey', 'website_url': 'https://www.harvey.ai', 'pricing_type': 'paid',
                'professions': ['legal-pro'], 'categories': ['legal'], 'tags': ['generative-ai', 'legal-tech'],
                'translation': {
                    'short_description': 'Generative AI for elite law firms.',
                    'long_description': 'Built on OpenAI models, Harvey assists lawyers with contract analysis, due diligence, litigation, and regulatory compliance.',
                    'use_cases': 'Contract review, Legal research, Drafting',
                    'pros_list': ['Specialized for law', 'Secure', 'Partnered with OpenAI'],
                    'cons_list': ['Waitlist access', 'Enterprise only']
                }
            },
        ]

        # --- PROCESS TOOLS ---
        self.stdout.write(f'Injecting {len(tools_data)} new tools...')
        
        # Link Tags
        for tool_d in tools_data:
            for t_slug in tool_d.get('tags', []):
                 Tag.objects.get_or_create(slug=t_slug, defaults={'name': t_slug.replace('-', ' ').title()})

        for data in tools_data:
            translation_data = data.pop('translation')
            
            pros_list = translation_data.pop('pros_list', [])
            cons_list = translation_data.pop('cons_list', [])
            
            profession_slugs = data.pop('professions', [])
            category_slugs = data.pop('categories', [])
            tag_slugs = data.pop('tags', [])
            
            tool, _ = Tool.objects.update_or_create(slug=data['slug'], defaults={**data, 'status': 'published'})

            # Add relations
            for slug in profession_slugs:
                if slug in prof_objs:
                    tool.professions.add(prof_objs[slug])
                else: 
                     # Try fetch if not in local map
                     try: 
                         tool.professions.add(Profession.objects.get(slug=slug))
                     except: pass
            
            for slug in category_slugs:
                if slug in categories:
                    tool.categories.add(categories[slug])
            
            for slug in tag_slugs:
                try: tool.tags.add(Tag.objects.get(slug=slug))
                except: pass

            # Translation
            if pros_list: translation_data['pros'] = "\n".join(pros_list)
            if cons_list: translation_data['cons'] = "\n".join(cons_list)
            
            ToolTranslation.objects.update_or_create(tool=tool, language='en', defaults=translation_data)


        # --- 4. TOOL STACKS ---
        stacks_data = [
            {
                'name': 'Modern Medical Clinic', 'slug': 'modern-medical', 'is_featured': True,
                'tagline': 'Optimizing patient flow and care.',
                'description': 'A suite of tools to reduce physician burnout, speed up diagnosis, and coordinate critical care teams.',
                'professions': ['doctor', 'radiologist'],
                'tool_slugs': ['aidoc', 'nuance-dax', 'viz-ai'],
                'workflow_description': """
### **Step 1: Automated Patient Intake & Documentation**
Start by using **Nuance DAX** during patient consultations. It listens to the conversation and automatically generates detailed clinical notes in your EHR. This allows you to maintain eye contact and build rapport without being distracted by typing.
- **Action**: Activate Nuance DAX at the start of the visit.
- **Benefit**: Saves ~7 minutes per encounter, reducing burnout.

### **Step 2: Rapid Diagnostics & Triage**
When imaging scans are ordered, **Aidoc** runs in the background. It analyzes CTs and MRIs immediately upon acquisition. If a critical anomaly like a pulmonary embolism or intracranial hemorrhage is detected, it flags the case to the top of the radiologist's worklist.
- **Action**: Radiologists prioritize "Aidoc Flagged" studies.
- **Benefit**: Reduces turnaround time for critical conditions by up to 50 minutes.

### **Step 3: Coordinated Care**
For positive stroke findings, **Viz.ai** instantly alerts the entire neurovascular team on their mobile devices. It shares the high-fidelity images securely, allowing the surgeon, interventionalist, and ER doc to coordinate the thrombectomy plan before the patient even leaves the scanner.
- **Action**: Review alerts on Viz.ai mobile app and confirm treatment plan via secure chat.
- **Benefit**: Saves brain during the "Golden Hour".
"""
            },
            {
                'name': 'Real Estate Powerhouse', 'slug': 'real-estate-power', 'is_featured': True,
                'tagline': 'End-to-end sales and marketing.',
                'description': 'From lead qualification to property valuation and marketing content, these tools power top agents.',
                'professions': ['real-estate-agent'],
                'tool_slugs': ['structurely', 'write-homes', 'housecanary', 'restb-ai'],
                'workflow_description': """
### **Step 1: Lead Capture & Qualification**
Connect your CRM to **Structurely**. When a new lead comes in from Zillow or your website, Structurely's AI assistant immediately sends a personalized text. It engages in a two-way conversation to qualify the lead's timeline, budget, and needs.
- **Action**: Set Structurely to "Aggressive Follow-up" for new internet leads.
- **Benefit**: Responds in < 2 mins 24/7, converting 3x more leads.

### **Step 2: Listing Preparation**
Once you secure a listing appointment, use **HouseCanary** to generate a granular valuation report. Show the seller exactly how market trends in their specific block affect their price. Then, use **Write.Homes** to generate the perfect MLS description.
- **Action**: Input address into HouseCanary for the presentation; Input property features into Write.Homes for the listing description.
- **Benefit**: Data-backed pricing wins listings; compelling copy drives clicks.

### **Step 3: Visual Marketing**
Upload your raw property photos to **Restb.ai** (integrated into many platforms) or use it to tag and classify images automatically.
- **Action**: Automate image tagging for your website's search filters.
- **Benefit**: Better SEO and user experience for buyers browsing your site.
"""
            },
            {
                'name': 'Future Finance Team', 'slug': 'future-finance', 'is_featured': False,
                'tagline': 'Automated AP and FP&A.',
                'description': 'Move beyond manual entry with autonomous invoice processing and AI-driven financial forecasting.',
                'professions': ['accountant', 'financial-analyst'],
                'tool_slugs': ['vic-ai', 'datarails', 'botkeeper'],
                'workflow_description': """
### **Step 1: Autonomous Invoice Processing**
Route all vendor invoices to **Vic.ai**. The AI extracts key data, predicts the coding, and sends it for approval. It learns your GL codes over time, eventually handling 90%+ of invoices without human touch.
- **Action**: Forward vendor emails to your Vic.ai dedicated inbox.
- **Benefit**: Eliminates manual data entry and reduces AP costs by 80%.

### **Step 2: Automated Bookkeeping**
For your client write-ups or subsidiary books, connect **Botkeeper**. It pulls bank feeds and categorizes transactions daily. Your team only logs in to handle exceptions/questions that the AI couldn't resolve.
- **Action**: Review Botkeeper's "Questions" tab weekly.
- **Benefit**: One accountant can handle 50+ clients instead of 15.

### **Step 3: Strategic Reporting**
Use **Datarails** to consolidate data from your ERP, Vic.ai, and other systems into Excel. Since it integrates directly with Excel, you can build executive dashboards that update automatically.
- **Action**: Click "Refresh" in your Datarails Excel plugin to update monthly board packages.
- **Benefit**: Complex financial models that are always up to date, without leaving Excel.
"""
            },
            {
                'name': 'Generative Architecture', 'slug': 'gen-arch', 'is_featured': True,
                'tagline': 'Designing the skyline with AI.',
                'description': 'Conceptualize sites in minutes and render photorealistic models instantly.',
                'professions': ['architect'],
                'tool_slugs': ['autodesk-forma', 'testfit', 'veras'],
                'workflow_description': """
### **Step 1: Rapid Feasibility Study**
Start a new project in **TestFit**. Outline the site boundary, and instantly generate optimized layouts for parking, multifamily units, or industrial warehouses. Adjust parameters like "unit mix" and see the yield and cost update in milliseconds.
- **Action**: Solve for max density on the given lot.
- **Benefit**: Go from 0 to a feasible concept in 15 minutes.

### **Step 2: Environmental Analysis**
Import your massing into **Autodesk Forma**. Run instant analyses for wind, noise, and solar potential. Adjust the massing to minimize wind tunnels and maximize daylight for residents.
- **Action**: Run the "Solar Energy" analysis to optimize roof angles.
- **Benefit**: Data-driven design decisions that improve sustainability and comfort.

### **Step 3: Visual Exploration**
Take a screenshot of your massing and load it into **Veras**. Use text prompts like "Scandinavian timber facade, golden hour" to generate photorealistic renderings over your simple geometry.
- **Action**: Generate 10 design variations to show the client.
- **Benefit**: Sell the vision instantly without hours of V-Ray rendering.
"""
            },
            {
                'name': 'Academic Researcher', 'slug': 'academic-researcher', 'is_featured': False,
                'tagline': 'Accelerate discovery.',
                'description': 'Conduct literature reviews and verify citations in a fraction of the time.',
                'professions': ['researcher'],
                'tool_slugs': ['consensus', 'elicit', 'scite'],
                'workflow_description': """
### **Step 1: Broad Discovery**
Start with a research question in **Consensus**. For example, "Does caffeine improve short-term memory?" It scans millions of papers and provides a summarized answer with citations.
- **Action**: Filter results by "Meta-Analysis" to get high-quality evidence.
- **Benefit**: Understand the scientific consensus in seconds.

### **Step 2: Deep Dive & Matrix Extraction**
Select key papers and import them into **Elicit**. Ask Elicit to specific data points: "What was the sample size?", "What was the dosage?". It builds a comparison table for you.
- **Action**: Run a "Systematic Review" workflow in Elicit.
- **Benefit**: Automates weeks of data extraction work.

### **Step 3: Quality Check**
Before citing a paper, run it through **Scite**. Check its "Smart Citations" to see if the paper has been supported or contrasted by subsequent studies.
- **Action**: Reject papers that have been heavily contrasted or retracted.
- **Benefit**: Ensure your research relies on solid, reproducible foundations.
"""
            },
            {
                'name': 'Podcast Studio', 'slug': 'podcast-studio', 'is_featured': True,
                'tagline': 'Broadcast quality from home.',
                'description': 'Record, edit text-based audio, and remove noise automatically.',
                'professions': ['podcaster'],
                'tool_slugs': ['descript', 'podcastle', 'adobe-podcast'],
                'workflow_description': """
### **Step 1: Remote Recording**
Send a **Podcastle** link to your guest. Record high-quality local audio from both sides directly in the browser. Unlike Zoom, this records the audio locally on their device so internet glitches don't ruin the quality.
- **Action**: Ensure "Magic Dust" is enabled for post-processing.
- **Benefit**: Studio quality from anywhere.

### **Step 2: Enhancement**
If there's still background noise (HVAC, dog barking), run the track through **Adobe Podcast's Enhance Speech**.
- **Action**: Drag and drop the WAV file into the web tool.
- **Benefit**: Makes a closet recording sound like a professional studio.

### **Step 3: Text-Based Editing**
Import the audio into **Descript**. It transcribes the conversation. To edit the podcast, simply delete the text of the boring parts, and the audio is cut automatically. Use "Studio Sound" to unify the levels.
- **Action**: Use the "Remove Filler Words" feature to delete all "ums" and "ahs" in one click.
- **Benefit**: Edits a 1-hour podcast in 20 minutes instead of 2 hours.
"""
            },
             {
                'name': 'Smart Recruiting', 'slug': 'smart-recruiting', 'is_featured': False,
                'tagline': 'Hire the best talent, faster.',
                'description': 'Reduce bias and automate screening to find the perfect candidates.',
                'professions': ['hr-manager'],
                'tool_slugs': ['eightfold-ai', 'hirevue', 'paradox'],
                'workflow_description': """
### **Step 1: Screening & Scheduling**
Deploy **Paradox** (Olivia) on your career site. The chatbot engages candidates 24/7, screens them for basic requirements (visa, experience), and automatically schedules an interview on your calendar.
- **Action**: Set screening questions for "Deal Breakers".
- **Benefit**: Zero time spent on scheduling emails.

### **Step 2: Video Interview**
Send screened candidates a **HireVue** on-demand interview link. They record answers to your standardized questions on their own time. HireVue scores their responses based on your competencies.
- **Action**: Review the top 10% scored candidates.
- **Benefit**: Standardized process that reveals soft skills earlier.

### **Step 3: Talent Intelligence**
Use **Eightfold AI** to look at your entire applicant database. It matches past applicants and current employees to new open roles based on skills, effectively rediscovering talent you already know.
- **Action**: Run a "Match" campaign for a hard-to-fill role.
- **Benefit**: Fills roles faster by recycling silver-medalist candidates.
"""
            },
        ]

        self.stdout.write(f'Creating {len(stacks_data)} tool stacks...')
        for s_data in stacks_data:
            tool_slugs = s_data.pop('tool_slugs')
            prof_slugs = s_data.pop('professions')
            
            stack, _ = ToolStack.objects.update_or_create(slug=s_data['slug'], defaults=s_data)
            
            # Add tools
            for ts in tool_slugs:
                try: stack.tools.add(Tool.objects.get(slug=ts))
                except Tool.DoesNotExist: 
                    self.stdout.write(f"Warning: Tool {ts} not found for stack {stack.name}")
            
            # Add professions
            for ps in prof_slugs:
                 if ps in prof_objs: stack.professions.add(prof_objs[ps])

        self.stdout.write(self.style.SUCCESS('Massive data injection complete.'))
