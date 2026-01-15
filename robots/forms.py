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
            'name': forms.TextInput(attrs={'class': 'neon-input w-full', 'placeholder': 'Boston Dynamics'}),
            'slug': forms.TextInput(attrs={'class': 'neon-input w-full', 'placeholder': 'boston-dynamics'}),
            'description': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 4}),
            'founded_year': forms.NumberInput(attrs={'class': 'neon-input w-full', 'placeholder': '2013'}),
            'headquarters': forms.TextInput(attrs={'class': 'neon-input w-full', 'placeholder': 'Waltham, MA, USA'}),
            'website': forms.URLInput(attrs={'class': 'neon-input w-full', 'placeholder': 'https://bostondynamics.com'}),
            'twitter_url': forms.URLInput(attrs={'class': 'neon-input w-full', 'placeholder': 'https://twitter.com/...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'neon-input w-full', 'placeholder': 'https://linkedin.com/...'}),
            'youtube_url': forms.URLInput(attrs={'class': 'neon-input w-full', 'placeholder': 'https://youtube.com/...'}),
            'meta_title': forms.TextInput(attrs={'class': 'neon-input w-full', 'maxlength': 60, 'placeholder': '50-60 chars'}),
            'meta_description': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 2, 'maxlength': 160, 'placeholder': '150-160 chars'}),
            'canonical_url': forms.URLInput(attrs={'class': 'neon-input w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
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
            # Status
            'status', 'is_featured',
            # SEO
            'meta_title', 'meta_description', 'og_image', 'canonical_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'neon-input w-full', 'placeholder': 'Tesla Optimus'}),
            'slug': forms.TextInput(attrs={'class': 'neon-input w-full', 'placeholder': 'tesla-optimus'}),
            'company': forms.Select(attrs={'class': 'select2'}),
            'product_url': forms.URLInput(attrs={'class': 'neon-input w-full', 'placeholder': 'https://...'}),
            'robot_type': forms.Select(attrs={'class': 'neon-input w-full'}),
            'target_market': forms.Select(attrs={'class': 'neon-input w-full'}),
            'release_date': forms.DateInput(attrs={'class': 'neon-input w-full', 'type': 'date'}),
            'availability': forms.Select(attrs={'class': 'neon-input w-full'}),
            'pricing_tier': forms.Select(attrs={'class': 'neon-input w-full'}),
            'price_value': forms.NumberInput(attrs={'class': 'neon-input w-full', 'placeholder': '20000.00'}),
            'short_description': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 2, 'maxlength': 300}),
            'long_description': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 6}),
            'pros': forms.Textarea(attrs={
                'class': 'neon-input w-full', 
                'rows': 3, 
                'placeholder': 'Advanced AI, Long battery life, Easy to use'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'neon-input w-full', 
                'rows': 3, 
                'placeholder': 'High price, Limited availability'
            }),
            'use_cases': forms.Textarea(attrs={
                'class': 'neon-input w-full', 
                'rows': 3, 
                'placeholder': 'Home assistance, Industrial automation, Research'
            }),
            'specifications': forms.Textarea(attrs={
                'class': 'neon-input w-full font-mono', 
                'rows': 4, 
                'placeholder': '{"height": "180cm", "weight": "70kg", "battery_life": "8h"}'
            }),
            'status': forms.Select(attrs={'class': 'neon-input w-full'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'neon-checkbox'}),
            'meta_title': forms.TextInput(attrs={'class': 'neon-input w-full', 'maxlength': 60}),
            'meta_description': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 2, 'maxlength': 160}),
            'canonical_url': forms.URLInput(attrs={'class': 'neon-input w-full'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
        
        # Specific overrides just in case
        self.fields['is_featured'].widget.attrs.update({'class': 'neon-checkbox'})
        self.fields['company'].widget.attrs.update({'class': 'select2'})

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
            'title': forms.TextInput(attrs={'class': 'neon-input w-full'}),
            'slug': forms.TextInput(attrs={'class': 'neon-input w-full'}),
            'excerpt': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 2, 'maxlength': 300}),
            'content': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 12}),
            'robots': forms.SelectMultiple(attrs={'class': 'select2', 'size': 6}),
            'source_name': forms.TextInput(attrs={'class': 'neon-input w-full', 'placeholder': 'TechCrunch'}),
            'source_url': forms.URLInput(attrs={'class': 'neon-input w-full'}),
            'published_at': forms.DateTimeInput(attrs={'class': 'neon-input w-full', 'type': 'datetime-local'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'neon-checkbox'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'neon-checkbox'}),
            'meta_title': forms.TextInput(attrs={'class': 'neon-input w-full', 'maxlength': 60}),
            'meta_description': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 2, 'maxlength': 160}),
            'canonical_url': forms.URLInput(attrs={'class': 'neon-input w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
        
        # Specific overrides
        self.fields['is_published'].widget.attrs.update({'class': 'neon-checkbox'})
        self.fields['is_featured'].widget.attrs.update({'class': 'neon-checkbox'})
        self.fields['robots'].widget.attrs.update({'class': 'select2'})
