from django import forms
from .models import Tool, ToolStack, Profession, Category, Tag

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = '__all__'
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
            self.fields[field].widget.attrs.update({'class': 'neon-input w-full'})
        # Specific overrides if needed
        self.fields['is_featured'].widget.attrs.update({'class': 'neon-checkbox'})
        # Improve widget for M2M fields to be more user friendly if select2 is not available immediately,
        # but the class 'neon-input' gives basic styling.

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
