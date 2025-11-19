from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    POST_TYPES = (
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('text', 'Text'),
        ('link', 'Link'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=10, choices=POST_TYPES)
    title = models.CharField(max_length=300)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='posts/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)
    restrict_to_group = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.post_type} - {self.group.name if self.group else 'Sitewide'}"

class ImageAttachment(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')
    caption = models.TextField(blank=True)

    def __str__(self):
        return f"Image for {self.post}"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user.username}"

class Vote(models.Model):
    VOTE_TYPES = (('up', 'Upvote'), ('down', 'Downvote'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=5, choices=VOTE_TYPES)

    class Meta:
        unique_together = ('user', 'post', 'comment')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.post:
            profile = self.post.user.profile
            profile.post_votes += 1 if self.vote_type == 'up' else -1
            profile.save()
        elif self.comment:
            profile = self.comment.user.profile
            profile.comment_votes += 1 if self.vote_type == 'up' else -1
            profile.save()

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('creator', 'Creator'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name} - {self.role}"

class ForumCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    is_public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Forum Categories'

    def __str__(self):
        return self.name

class Forum(models.Model):
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='forums')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sub_forums')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Forums'

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    forum = models.ForeignKey(Forum, related_name='posts', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} by {self.user.username}"