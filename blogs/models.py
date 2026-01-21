from django.db import models
from django.utils.text import slugify
from tools.models import Tool, ToolStack, Profession, Tag
from robots.models import Robot

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    # Connections
    tags = models.ManyToManyField(Tag, blank=True, related_name='blog_posts')
    tools = models.ManyToManyField(Tool, blank=True, related_name='blog_posts')
    stacks = models.ManyToManyField(ToolStack, blank=True, related_name='blog_posts')
    professions = models.ManyToManyField(Profession, blank=True, related_name='blog_posts')
    robots = models.ManyToManyField(Robot, blank=True, related_name='blog_posts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Always generate slug from title + date (YYYYMMDD)
        from django.utils import timezone
        if not self.pk:
            # For new posts, use current date
            date_str = timezone.now().strftime('%Y%m%d')
        else:
            # For existing posts, use original creation date
            date_str = self.created_at.strftime('%Y%m%d')
        
        base_slug = slugify(self.title)
        self.slug = f"{date_str}-{base_slug}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})

    @property
    def first_image(self):
        first_chapter = self.chapters.order_by('order').first()
        if first_chapter:
            return first_chapter.image
        return None

    @property
    def first_text(self):
        first_chapter = self.chapters.order_by('order').first()
        if first_chapter:
            return first_chapter.text
        return ""

class BlogChapter(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='chapters')
    image = models.ImageField(upload_to='blog_images/')
    text = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.blog_post.title} - Chapter {self.order}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image:
            from PIL import Image, ImageOps
            import os

            try:
                img_path = self.image.path
                if os.path.exists(img_path):
                    with Image.open(img_path) as img:
                        # Check if already square to save resources
                        width, height = img.size
                        if width != height:
                            # Determine size (use the smaller dimension for max quality square)
                            size = min(width, height)
                            
                            # Crop to square
                            new_img = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS)
                            
                            # Save back to same path
                            new_img.save(img_path)
            except Exception as e:
                print(f"Error cropping blog chapter image: {e}")
