"""
AI Service for Robot Bulk Import.
Uses Gemini to generate robot metadata from CSV data.
"""

import json
import re
from django.conf import settings

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class RobotAIService:
    """Service for AI-powered robot metadata generation."""
    
    # Map pricing text patterns to pricing_tier choices
    PRICING_PATTERNS = {
        'consumer': ['consumer', '$1k', '$3k', '$5k', '$10k', 'retail', '~$', 'approximately'],
        'prosumer': ['prosumer', '$10k', '$20k', '$30k', '$50k'],
        'professional': ['professional', '$50k', '$100k', '$200k', 'enterprise'],
        'enterprise': ['enterprise', '$200k', '$300k+', 'contract', 'custom', 'bespoke', 'undisclosed'],
        'lease': ['lease', 'subscription', 'monthly'],
    }
    
    @classmethod
    def map_pricing_text(cls, pricing_text):
        """Map CSV pricing text to pricing_tier choice."""
        if not pricing_text:
            return 'unknown'
        
        pricing_lower = pricing_text.lower()
        
        for tier, patterns in cls.PRICING_PATTERNS.items():
            for pattern in patterns:
                if pattern in pricing_lower:
                    return tier
        
        return 'unknown'
    
    @staticmethod
    def generate_robot_metadata(robot_name, product_url, short_description, 
                                 long_description, pricing_text, company_name):
        """
        Uses Gemini to generate complete robot metadata for bulk import.
        Returns a dictionary with all required fields.
        """
        if not GENAI_AVAILABLE or not settings.GEMINI_API_KEY:
            # Fallback response when AI is unavailable
            return {
                'error': 'No API key configured' if not settings.GEMINI_API_KEY else 'genai not available',
                'robot_type': 'humanoid',
                'target_market': 'industry',
                'availability': 'announced',
                'pricing_tier': RobotAIService.map_pricing_text(pricing_text),
                'pros': '',
                'cons': '',
                'use_cases': '',
                'meta_title': f"{robot_name} - AI Robot by {company_name}",
                'meta_description': short_description[:160] if short_description else '',
            }
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        system_instruction = """
You are an expert AI robotics analyst and SEO specialist.
You have access to Google Search. Use it to verify the robot's specifications, availability, and current status.

Your task is to analyze the robot and produce:

1. robot_type: Exactly one of: "humanoid" or "specialized"
   - "humanoid" = bipedal human-like form factor
   - "specialized" = drones, industrial arms, wheeled robots, etc.

2. target_market: Exactly one of: "home", "industry", "medical", "service", "military", "research"

3. availability: Exactly one of: "available", "preorder", "announced", "development", "prototype", "discontinued"

4. pricing_tier: Exactly one of: "unknown", "consumer", "prosumer", "professional", "enterprise", "lease"
   - consumer = $1K - $10K
   - prosumer = $10K - $50K
   - professional = $50K - $200K
   - enterprise = $200K+
   - lease = rental/subscription only

5. use_cases: 3-5 specific use cases, comma-separated. Be practical and specific to this robot.

6. pros: 3-5 advantages of this robot, comma-separated. Be specific and value-focused.

7. cons: 2-3 potential downsides or limitations, comma-separated. Be honest but fair.

8. meta_title: SEO title, 50-60 characters. Include robot name and key benefit.

9. meta_description: SEO description, 150-160 characters. Compelling summary with call to action.

Output MUST be valid JSON only. No markdown, no explanation.
"""

        prompt = f"""
ROBOT INFORMATION:
- Name: {robot_name}
- Company: {company_name}
- Product URL: {product_url}
- Short Description: {short_description}
- Detailed Description: {long_description}
- Pricing Info from CSV: {pricing_text}

Generate the complete metadata JSON for this robot. Use search to verify details.
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
            
            # Extract JSON from response text
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(response_text)
            
            # Validate and normalize response
            result = {
                'robot_type': data.get('robot_type', 'humanoid'),
                'target_market': data.get('target_market', 'industry'),
                'availability': data.get('availability', 'announced'),
                'pricing_tier': data.get('pricing_tier', 'unknown'),
                'use_cases': data.get('use_cases', ''),
                'pros': data.get('pros', ''),
                'cons': data.get('cons', ''),
                'meta_title': data.get('meta_title', f"{robot_name} - AI Robot")[:200],
                'meta_description': data.get('meta_description', short_description[:160] if short_description else ''),
            }
            
            # Ensure robot_type is valid
            if result['robot_type'] not in ['humanoid', 'specialized']:
                result['robot_type'] = 'humanoid'
            
            # Ensure target_market is valid
            valid_targets = ['home', 'industry', 'medical', 'service', 'military', 'research']
            if result['target_market'] not in valid_targets:
                result['target_market'] = 'industry'
            
            # Ensure availability is valid
            valid_availability = ['available', 'preorder', 'announced', 'development', 'prototype', 'discontinued']
            if result['availability'] not in valid_availability:
                result['availability'] = 'announced'
            
            # Ensure pricing_tier is valid
            valid_pricing = ['unknown', 'consumer', 'prosumer', 'professional', 'enterprise', 'lease']
            if result['pricing_tier'] not in valid_pricing:
                result['pricing_tier'] = RobotAIService.map_pricing_text(pricing_text)
            
            # Convert lists to comma-separated if needed
            if isinstance(result['use_cases'], list):
                result['use_cases'] = ', '.join(result['use_cases'])
            if isinstance(result['pros'], list):
                result['pros'] = ', '.join(result['pros'])
            if isinstance(result['cons'], list):
                result['cons'] = ', '.join(result['cons'])
            
            return result
            
        except Exception as e:
            # Return fallback on any error
            return {
                'error': str(e),
                'robot_type': 'humanoid',
                'target_market': 'industry',
                'availability': 'announced',
                'pricing_tier': RobotAIService.map_pricing_text(pricing_text),
                'pros': '',
                'cons': '',
                'use_cases': '',
                'meta_title': f"{robot_name} - AI Robot by {company_name}",
                'meta_description': short_description[:160] if short_description else '',
            }
