"""
Forms for the robots app.
ModelForms for Robot, RobotCompany, and RobotNews with SEO field sections.
"""

from django import forms
from .models import Robot, RobotCompany, RobotNews


class RobotCompanyForm(forms.ModelForm):
    """Form for creating/editing robot companies."""
    
    class Meta:
        model = RobotCompany
        fields = [
            'name', 'slug', 'logo', 'description',
            'founded_year', 'headquarters', 'website',
            'twitter_url', 'linkedin_url', 'youtube_url',
            'meta_title', 'meta_description', 'og_image', 'canonical_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Boston Dynamics'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'boston-dynamics'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '2013'}),
            'headquarters': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Waltham, MA, USA'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://bostondynamics.com'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://twitter.com/...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://linkedin.com/...'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://youtube.com/...'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-input', 'maxlength': 60, 'placeholder': '50-60 chars'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'maxlength': 160, 'placeholder': '150-160 chars'}),
            'canonical_url': forms.URLInput(attrs={'class': 'form-input'}),
        }


class RobotForm(forms.ModelForm):
    """Form for creating/editing robots with all fields including SEO."""
    
    class Meta:
        model = Robot
        fields = [
            # Basic
            'name', 'slug', 'company', 'product_url', 'image',
            # Classification
            'robot_type', 'target_market',
            # Release & Pricing
            'release_date', 'availability', 'pricing_tier', 'price_value',
            # Content
            'short_description', 'long_description', 'pros', 'cons', 'use_cases',
            # Technical
            'specifications',
            # Integrations
            'compatible_tools',
            # Status
            'status', 'is_featured',
            # SEO
            'meta_title', 'meta_description', 'og_image', 'canonical_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tesla Optimus'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'tesla-optimus'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'product_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'robot_type': forms.Select(attrs={'class': 'form-select'}),
            'target_market': forms.Select(attrs={'class': 'form-select'}),
            'release_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'pricing_tier': forms.Select(attrs={'class': 'form-select'}),
            'price_value': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '20000.00'}),
            'short_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'maxlength': 300}),
            'long_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6}),
            'pros': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3, 
                'placeholder': 'Advanced AI, Long battery life, Easy to use'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3, 
                'placeholder': 'High price, Limited availability'
            }),
            'use_cases': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'rows': 3, 
                'placeholder': 'Home assistance, Industrial automation, Research'
            }),
            'specifications': forms.Textarea(attrs={
                'class': 'form-textarea font-mono', 
                'rows': 4, 
                'placeholder': '{"height": "180cm", "weight": "70kg", "battery_life": "8h"}'
            }),
            'compatible_tools': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-input', 'maxlength': 60}),
            'meta_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'maxlength': 160}),
            'canonical_url': forms.URLInput(attrs={'class': 'form-input'}),
        }
    
    def clean_specifications(self):
        """Validate that specifications is valid JSON."""
        specs = self.cleaned_data.get('specifications')
        if isinstance(specs, str):
            try:
                import json
                specs = json.loads(specs)
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON format for specifications')
        return specs


class RobotNewsForm(forms.ModelForm):
    """Form for creating/editing robot news articles."""
    
    class Meta:
        model = RobotNews
        fields = [
            'title', 'slug', 'excerpt', 'content',
            'featured_image',
            'robots',
            'source_name', 'source_url',
            'published_at', 'is_published', 'is_featured',
            'meta_title', 'meta_description', 'og_image', 'canonical_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'maxlength': 300}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 12}),
            'robots': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'source_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'TechCrunch'}),
            'source_url': forms.URLInput(attrs={'class': 'form-input'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-input', 'maxlength': 60}),
            'meta_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'maxlength': 160}),
            'canonical_url': forms.URLInput(attrs={'class': 'form-input'}),
        }
