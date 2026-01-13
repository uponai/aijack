from django import forms
from .models import Tool, ToolStack, Profession, Category, Tag, SubmittedTool

class ToolForm(forms.ModelForm):
    # Translation fields
    short_description = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'class': 'neon-input w-full'}), help_text="English Short Description")
    long_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 4}), help_text="English Long Description")
    use_cases = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 3}), help_text="Comma-separated use cases (English)")
    pros = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 3}), help_text="Comma-separated pros (English)")
    cons = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 3}), help_text="Comma-separated cons (English)")

    class Meta:
        model = Tool
        fields = ['name', 'slug', 'website_url', 'affiliate_url', 'pricing_type', 'status', 'logo', 
                  'is_featured', 'highlight_start', 'highlight_end', 'categories', 'professions', 'tags',
                  'meta_title', 'meta_description', 'og_image', 'canonical_url']
        widgets = {
            'highlight_start': forms.DateInput(attrs={'type': 'date'}),
            'highlight_end': forms.DateInput(attrs={'type': 'date'}),
            'categories': forms.SelectMultiple(attrs={'class': 'select2'}),
            'professions': forms.SelectMultiple(attrs={'class': 'select2'}),
            'tags': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
        
        # Specific overrides
        self.fields['is_featured'].widget.attrs.update({'class': 'neon-checkbox'})
        
        # Prefill translation fields if editing
        if self.instance and self.instance.pk:
            trans = self.instance.get_translation('en')
            if trans:
                self.fields['short_description'].initial = trans.short_description
                self.fields['long_description'].initial = trans.long_description
                self.fields['use_cases'].initial = trans.use_cases
                self.fields['pros'].initial = trans.pros
                self.fields['cons'].initial = trans.cons

    def save(self, commit=True):
        tool = super().save(commit=False)
        if commit:
            tool.save()
            self.save_m2m()
            
            # Save English Translation
            from .models import ToolTranslation
            ToolTranslation.objects.update_or_create(
                tool=tool,
                language='en',
                defaults={
                    'short_description': self.cleaned_data.get('short_description'),
                    'long_description': self.cleaned_data.get('long_description'),
                    'use_cases': self.cleaned_data.get('use_cases'),
                    'pros': self.cleaned_data.get('pros'),
                    'cons': self.cleaned_data.get('cons'),
                }
            )
        return tool

class ToolStackForm(forms.ModelForm):
    class Meta:
        model = ToolStack
        fields = ['name', 'slug', 'tagline', 'description', 'workflow_description', 'visibility', 'tools', 'professions', 'is_featured', 'highlight_start', 'highlight_end', 'owner']
        widgets = {
            'highlight_start': forms.DateInput(attrs={'type': 'date'}),
            'highlight_end': forms.DateInput(attrs={'type': 'date'}),
            'tools': forms.SelectMultiple(attrs={'class': 'select2'}),
            'professions': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
        self.fields['is_featured'].widget.attrs.update({'class': 'neon-checkbox'})

class ProfessionForm(forms.ModelForm):
    class Meta:
        model = Profession
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})

class ToolSubmissionForm(forms.ModelForm):
    class Meta:
        model = SubmittedTool
        fields = ['name', 'website_url', 'recommended_profession', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
