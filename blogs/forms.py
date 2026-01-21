from django import forms
from django.forms import inlineformset_factory
from .models import BlogPost, BlogChapter

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'is_published', 'tags', 'tools', 'stacks', 'professions', 'robots']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'neon-input w-full font-heading font-bold text-lg'}),
            'slug': forms.TextInput(attrs={'class': 'neon-input w-full font-mono text-sm text-slate-500'}),
            'tags': forms.SelectMultiple(attrs={'class': 'select2'}),
            'tools': forms.SelectMultiple(attrs={'class': 'select2'}),
            'stacks': forms.SelectMultiple(attrs={'class': 'select2'}),
            'professions': forms.SelectMultiple(attrs={'class': 'select2'}),
            'robots': forms.SelectMultiple(attrs={'class': 'select2'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'neon-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure 'class' attribute exists for fields that might not have it set in widgets
        if 'is_published' in self.fields:
             self.fields['is_published'].widget.attrs.update({'class': 'neon-checkbox'})


class BlogChapterForm(forms.ModelForm):
    class Meta:
        model = BlogChapter
        fields = ['image', 'text', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-pink-50 file:text-pink-700 hover:file:bg-pink-100'}),
            'text': forms.Textarea(attrs={'class': 'neon-input w-full', 'rows': 4, 'placeholder': 'Write your post chapter here...'}),
            'order': forms.NumberInput(attrs={'class': 'neon-input w-20', 'min': 0}),
        }

BlogChapterFormSet = inlineformset_factory(
    BlogPost, BlogChapter, form=BlogChapterForm,
    extra=0, can_delete=True, min_num=1, validate_min=True
)
