import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post, Comment, Vote, ImageAttachment, Group, GroupMembership, ForumCategory, Forum, ForumPost
from users.models import Notification
from .forms import PostForm, CommentForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
import mimetypes
import magic
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
import os
from rest_framework import viewsets, serializers
import ffmpeg
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.text import slugify
from django import forms

logger = logging.getLogger(__name__)

class ProfilePost:
    def __init__(self, title, user, created_at):
        self.title = title
        self.user = user
        self.created_at = created_at

class AdminPost:
    def __init__(self, title, created_at):
        self.title = title
        self.created_at = created_at

def home(request):
    sort_by = request.GET.get('sort', 'all')
    time_filters = {
        'day': timezone.now() - timedelta(days=1),
        'week': timezone.now() - timedelta(weeks=1),
        'month': timezone.now() - timedelta(days=30),
        'year': timezone.now() - timedelta(days=365),
        'all': None,
    }
    start_date = time_filters.get(sort_by)

    base_query = Post.objects.filter(is_hidden=False, restrict_to_group=False)
    if start_date:
        base_query = base_query.filter(created_at__gte=start_date)

    image_posts = base_query.filter(post_type='image').order_by('-votes')[:12]
    video_posts = base_query.filter(post_type='video').order_by('-votes')[:12]
    audio_posts = base_query.filter(post_type='audio').order_by('-votes')[:12]
    text_link_posts = base_query.filter(post_type__in=['text', 'link']).order_by('-votes')[:12]

    text_count = base_query.filter(post_type='text').count()
    link_count = base_query.filter(post_type='link').count()
    print(f"Text posts: {text_count}, Link posts: {link_count}")

    admin_posts = [
        AdminPost(
            title=f"Admin Update {i + 1} - Breaking news from the team!",
            created_at=timezone.now() - timedelta(hours=i * 5)
        )
        for i in range(3)
    ]

    user = User.objects.first()
    user_posts = []
    if user:
        user_posts = [
            ProfilePost(
                title=f"User Blog Post {i + 1}",
                user=user,
                created_at=timezone.now() - timedelta(days=i)
            )
            for i in range(3)
        ]

    context = {
        'sort_by': sort_by,
        'image_posts': image_posts,
        'video_posts': video_posts,
        'audio_posts': audio_posts,
        'text_link_posts': text_link_posts,
        'admin_posts': admin_posts,
        'user_posts': user_posts,
    }
    return render(request, 'core/home.html', context)

def images(request):
    sort_by = request.GET.get('sort', 'all')
    time_filters = {
        'day': timezone.now() - timedelta(days=1),
        'week': timezone.now() - timedelta(weeks=1),
        'month': timezone.now() - timedelta(days=30),
        'year': timezone.now() - timedelta(days=365),
        'all': None,
    }
    start_date = time_filters.get(sort_by)

    base_query = Post.objects.filter(post_type='image', restrict_to_group=False)
    if start_date:
        base_query = base_query.filter(created_at__gte=start_date)

    posts = base_query.order_by('-votes')
    paginator = Paginator(posts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    return render(request, 'core/images.html', context)

def videos(request):
    sort_by = request.GET.get('sort', 'all')
    time_filters = {
        'day': timezone.now() - timedelta(days=1),
        'week': timezone.now() - timedelta(weeks=1),
        'month': timezone.now() - timedelta(days=30),
        'year': timezone.now() - timedelta(days=365),
        'all': None,
    }
    start_date = time_filters.get(sort_by)

    base_query = Post.objects.filter(post_type='video', restrict_to_group=False)
    if start_date:
        base_query = base_query.filter(created_at__gte=start_date)

    posts = base_query.order_by('-votes')
    paginator = Paginator(posts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    return render(request, 'core/videos.html', context)

def audio(request):
    sort_by = request.GET.get('sort', 'all')
    time_filters = {
        'day': timezone.now() - timedelta(days=1),
        'week': timezone.now() - timedelta(weeks=1),
        'month': timezone.now() - timedelta(days=30),
        'year': timezone.now() - timedelta(days=365),
        'all': None,
    }
    start_date = time_filters.get(sort_by)

    base_query = Post.objects.filter(post_type='audio', restrict_to_group=False)
    if start_date:
        base_query = base_query.filter(created_at__gte=start_date)

    posts = base_query.order_by('-votes')
    paginator = Paginator(posts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    return render(request, 'core/audio.html', context)

def text_links(request):
    sort_by = request.GET.get('sort', 'all')
    time_filters = {
        'day': timezone.now() - timedelta(days=1),
        'week': timezone.now() - timedelta(weeks=1),
        'month': timezone.now() - timedelta(days=30),
        'year': timezone.now() - timedelta(days=365),
        'all': None,
    }
    start_date = time_filters.get(sort_by)

    base_query = Post.objects.filter(post_type__in=['text', 'link'], restrict_to_group=False)
    if start_date:
        base_query = base_query.filter(created_at__gte=start_date)

    posts = base_query.order_by('-votes')
    paginator = Paginator(posts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    return render(request, 'core/text_links.html', context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            if post.user != request.user:
                comment_link = reverse('direct_comment', args=[comment.id])
                post_link = reverse('post_detail', args=[post.id])
                notification = Notification.objects.create(
                    user=post.user,
                    message=f"{request.user.username} commented on your post: <a href='{comment_link}'>{comment.content}</a>",
                    link=post_link
                )
                logger.info(f"Sending notification to user {post.user.id}")
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{post.user.id}',
                    {
                        'type': 'send_notification',
                        'message': f"{request.user.username} commented on your post: <a href='{comment_link}'>{comment.content}</a>",
                        'post_link': post_link,
                        'post_title': post.title,
                        'created_at': notification.created_at.isoformat(),
                    }
                )
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()
    top_level_comments = post.comments.filter(parent__isnull=True)
    return render(request, 'core/post_detail.html',
                  {'post': post, 'form': form, 'top_level_comments': top_level_comments})

@login_required
def reply_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = parent_comment.post
            comment.user = request.user
            comment.parent = parent_comment
            comment.save()
            if parent_comment.user != request.user:
                Notification.objects.create(
                    user=parent_comment.user,
                    message=f"{request.user.username} replied to your comment",
                    link=reverse('direct_comment', args=[parent_comment.id])
                )
            return redirect('direct_comment', comment_id=comment_id)
    return redirect('direct_comment', comment_id=comment_id)

@login_required
def upload_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        if post_id:
            try:
                post = Post.objects.get(id=post_id)
                if 'thumbnail' in request.FILES:
                    post.thumbnail = request.FILES['thumbnail']
                    post.save()
                    return JsonResponse({'success': True, 'post_id': post.id})
                return JsonResponse({'success': False, 'error': 'No thumbnail provided'})
            except Post.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Post not found'})

        post_type = request.POST.get('post_type')
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        link_url = request.POST.get('url', '')
        group_id = request.POST.get('group_id')
        restrict_to_group = request.POST.get('restrict_to_group', 'off') == 'on'

        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'})
        if post_type == 'link' and not link_url:
            return JsonResponse({'success': False, 'error': 'URL is required for link posts'})
        if post_type == 'image' and 'files' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'At least one image is required'})
        if group_id and not GroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
            return JsonResponse({'success': False, 'error': 'You are not a member of this group'})

        post = Post(
            post_type=post_type,
            title=title,
            user=request.user,
            group=Group.objects.get(id=group_id) if group_id else None,
            restrict_to_group=restrict_to_group
        )

        if post_type == 'text' and content:
            post.content = content
        elif post_type == 'link':
            post.link = link_url
        elif post_type == 'audio' and 'audio_file' in request.FILES:
            post.file = request.FILES['audio_file']
        elif post_type == 'video':
            if 'video_file' in request.FILES:
                post.file = request.FILES['video_file']
                post.save()
                try:
                    video_path = post.file.path
                    thumbnail_path = os.path.join('media/thumbnails', f"thumbnail_{post.id}.jpg")
                    stream = ffmpeg.input(video_path).filter('select', 'eq(n,30)')
                    stream = ffmpeg.output(stream, thumbnail_path, vframes=1, format='image2', loglevel='error')
                    ffmpeg.run(stream, overwrite_output=True)
                    with open(thumbnail_path, 'rb') as f:
                        post.thumbnail.save(os.path.basename(thumbnail_path), ContentFile(f.read()), save=False)
                    os.remove(thumbnail_path)
                except Exception as e:
                    logger.error(f"Video thumbnail generation failed for post {post.id}: {e}")
            elif request.POST.get('video_url'):
                post.video_url = request.POST.get('video_url')
                post.save()

        if 'thumbnail' in request.FILES:
            post.thumbnail = request.FILES['thumbnail']
        elif post_type == 'link':
            if not link_url.startswith(('http://', 'https://')):
                link_url = 'http://' + link_url
            try:
                response = requests.get(link_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    og_image = soup.find('meta', property='og:image')
                    thumbnail_url = og_image['content'] if og_image else None
                    if thumbnail_url:
                        img_response = requests.get(thumbnail_url, timeout=5)
                        if img_response.status_code == 200:
                            img_name = os.path.basename(thumbnail_url) or 'link_thumbnail.jpg'
                            post.thumbnail.save(img_name, ContentFile(img_response.content), save=False)
            except Exception as e:
                print(f"Thumbnail scrape failed: {e}")
        elif post_type == 'video' and 'video_file' in request.FILES:
            try:
                video_path = post.file.path
                thumbnail_path = os.path.join('media/thumbnails', f"thumbnail_{post.id}.jpg")
                stream = ffmpeg.input(video_path).filter('select', 'eq(n,30)')
                stream = ffmpeg.output(stream, thumbnail_path, vframes=1, format='image2', loglevel='error')
                ffmpeg.run(stream, overwrite_output=True)
                with open(thumbnail_path, 'rb') as f:
                    post.thumbnail.save(os.path.basename(thumbnail_path), ContentFile(f.read()), save=False)
                os.remove(thumbnail_path)
            except Exception as e:
                print(f"Video thumbnail generation failed: {e}")
        elif post_type == 'image' and 'files' in request.FILES:
            first_image = request.FILES.getlist('files')[0]
            post.thumbnail.save(f"thumbnail_{post.id}.jpg", first_image, save=False)

        post.save()

        if post_type == 'image':
            for image_file in request.FILES.getlist('files'):
                ImageAttachment.objects.create(post=post, image=image_file)

        return JsonResponse({'success': True, 'post_id': post.id})

    return render(request, 'core/upload.html', {'type': request.GET.get('type', 'text')})

@login_required
def vote_post(request, post_id, vote_type):
    post = Post.objects.get(id=post_id)
    vote, created = Vote.objects.get_or_create(user=request.user, post=post)
    if vote.vote_type != vote_type:
        vote.vote_type = vote_type
        vote.save()
        post.votes += 1 if vote_type == 'up' else -1
        post.save()
    return redirect('post_detail', post_id=post_id)

@login_required
def vote_comment(request, comment_id, vote_type):
    comment = Comment.objects.get(id=comment_id)
    vote, created = Vote.objects.get_or_create(user=request.user, comment=comment)
    if vote.vote_type != vote_type:
        vote.vote_type = vote_type
        vote.save()
        comment.votes += 1 if vote_type == 'up' else -1
        comment.save()
    return redirect('post_detail', post_id=comment.post.id)

@login_required
def hide_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.profile.group == 'admin' or request.user == post.user:
        post.is_hidden = True
        post.save()
    return redirect('post_detail', post_id=post_id)

@login_required
def perm_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.profile.group == 'admin' or request.user == post.user:
        post.delete()
    return redirect('home')

@login_required
def hide_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.profile.group == 'admin' or request.user == comment.user:
        comment.is_hidden = True
        comment.save()
    return redirect('post_detail', post_id=comment.post.id)

@login_required
def perm_delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.profile.group == 'admin' or request.user == comment.user:
        comment.delete()
    return redirect('post_detail', post_id=comment.post.id)

@login_required
def mod_panel(request):
    if request.user.profile.group != 'admin':
        return redirect('home')
    hidden_posts = Post.objects.filter(is_hidden=True)
    hidden_comments = Comment.objects.filter(is_hidden=True)
    return render(request, 'core/mod_panel.html', {
        'hidden_posts': hidden_posts,
        'hidden_comments': hidden_comments,
    })

def direct_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    return redirect('post_detail', post_id=comment.post.id)

# Forum views
def forums(request):
    categories = ForumCategory.objects.all()  # Include private categories for admins
    for category in categories:
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.group == 'admin':
            # Admins see all top-level forums (parent is null)
            category.filtered_forums = category.forums.filter(parent__isnull=True)
        else:
            # Regular users see public, non-hidden top-level forums
            category.filtered_forums = category.forums.filter(is_hidden=False, is_public=True, parent__isnull=True)
        for forum in category.filtered_forums:
            if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.group == 'admin':
                forum.filtered_sub_forums = forum.sub_forums.all()
            else:
                forum.filtered_sub_forums = forum.sub_forums.filter(is_hidden=False, is_public=True)
    context = {
        'categories': categories,
    }
    return render(request, 'core/forums.html', context)

@login_required
def create_forum(request):
    if not hasattr(request.user, 'profile') or request.user.profile.group != 'admin':
        return redirect('forums')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public', 'on') == 'on'
        parent_type = request.POST.get('parent_type')
        parent_id = request.POST.get('parent_id')

        logger.info(f"Creating with parent_type: {parent_type}, parent_id: {parent_id}, title: {title}")

        if not title:
            return render(request, 'core/create_forum.html', {
                'error': 'Title is required',
                'categories': ForumCategory.objects.all(),
                'forums': Forum.objects.all(),
            })

        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        if not parent_type or parent_type == 'none':  # Create a category
            while ForumCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            category = ForumCategory(
                name=title,
                description=description,
                slug=slug,
                is_public=is_public
            )
            category.save()
            logger.info(f"Created category: {category.name} (slug: {category.slug}, public: {category.is_public})")
            return redirect('forums')
        elif parent_type == 'category':  # Create a forum
            while Forum.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            if parent_id.startswith('category_'):
                parent_id = parent_id.replace('category_', '')
            category = get_object_or_404(ForumCategory, id=parent_id)
            forum = Forum(
                category=category,
                title=title,
                description=description,
                slug=slug,
                created_by=request.user,
                is_public=is_public
            )
            forum.save()
            logger.info(f"Created forum: {forum.title} in category {category.name} (slug: {forum.slug}, public: {forum.is_public})")
            return redirect('forum_detail', forum_slug=forum.slug)
        else:  # Create a sub-forum
            while Forum.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            if parent_id.startswith('forum_'):
                parent_id = parent_id.replace('forum_', '')
            parent_forum = get_object_or_404(Forum, id=parent_id)
            forum = Forum(
                category=parent_forum.category,
                title=title,
                description=description,
                slug=slug,
                parent=parent_forum,
                created_by=request.user,
                is_public=is_public
            )
            forum.save()
            logger.info(f"Created sub-forum: {forum.title} under {parent_forum.title} (slug: {forum.slug}, public: {forum.is_public})")
            return redirect('forum_detail', forum_slug=forum.slug)

    return render(request, 'core/create_forum.html', {
        'categories': ForumCategory.objects.all(),
        'forums': Forum.objects.all(),
    })

def forum_detail(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug, is_hidden=False)
    if not forum.is_public and not request.user.is_authenticated:
        return redirect('login')

    sub_forums = forum.sub_forums.filter(is_hidden=False, is_public=True)
    posts = forum.posts.filter(is_hidden=False, parent__isnull=True).order_by('-is_pinned', 'created_at')
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'forum': forum,
        'sub_forums': sub_forums,
        'page_obj': page_obj,
    }
    return render(request, 'core/forum_detail.html', context)

class ForumPostForm(forms.ModelForm):
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ForumPost
        fields = ['title', 'content', 'parent_id']
        widgets = {
            'title': forms.TextInput(attrs={'id': 'id_title'}),
            'content': forms.Textarea(attrs={'id': 'id_content'}),
        }

@login_required
def create_forum_post(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug, is_hidden=False)
    if forum.is_locked:
        return redirect('forum_detail', forum_slug=forum.slug)

    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.forum = forum
            post.user = request.user
            parent_id = form.cleaned_data['parent_id']
            logger.info(f"Creating post in forum {forum.slug}, parent_id: {parent_id}, title: {post.title}")
            if parent_id:
                try:
                    post.parent = ForumPost.objects.get(id=parent_id, forum=forum)
                    logger.info(f"Set parent to post {post.parent.id} for reply {post.title}")
                except ForumPost.DoesNotExist:
                    logger.warning(f"Parent post {parent_id} not found for reply {post.title}")
                    post.parent = None
            post.save()
            logger.info(f"Saved post {post.id} (title: {post.title}, parent_id: {post.parent_id})")

            # Notify thread creator (first post) and parent post owner (if reply)
            thread_starter = ForumPost.objects.filter(forum=forum, parent__isnull=True).order_by('created_at').first()
            if thread_starter and thread_starter.user != request.user:
                Notification.objects.create(
                    user=thread_starter.user,
                    message=f"{request.user.username} posted in your thread: <a href='{reverse('forum_post_detail', args=[forum.slug, post.id])}'>{post.title}</a>",
                    link=reverse('forum_post_detail', args=[forum.slug, post.id])
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{thread_starter.user.id}',
                    {
                        'type': 'send_notification',
                        'message': f"{request.user.username} posted in your thread: <a href='{reverse('forum_post_detail', args=[forum.slug, post.id])}'>{post.title}</a>",
                        'post_link': reverse('forum_post_detail', args=[forum.slug, post.id]),
                        'post_title': post.title,
                        'created_at': post.created_at.isoformat(),
                    }
                )
            if post.parent and post.parent.user != request.user:
                Notification.objects.create(
                    user=post.parent.user,
                    message=f"{request.user.username} replied to your post: <a href='{reverse('forum_post_detail', args=[forum.slug, post.id])}'>{post.title}</a>",
                    link=reverse('forum_post_detail', args=[forum.slug, post.id])
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{post.parent.user.id}',
                    {
                        'type': 'send_notification',
                        'message': f"{request.user.username} replied to your post: <a href='{reverse('forum_post_detail', args=[forum.slug, post.id])}'>{post.title}</a>",
                        'post_link': reverse('forum_post_detail', args=[forum.slug, post.id]),
                        'post_title': post.title,
                        'created_at': post.created_at.isoformat(),
                    }
                )

            return redirect('forum_post_detail', forum_slug=forum.slug, post_id=post.id)
    else:
        parent_id = request.GET.get('parent_id')
        initial = {'parent_id': parent_id} if parent_id else {}
        form = ForumPostForm(initial=initial)

    parent_post = None
    if initial.get('parent_id'):
        try:
            parent_post = ForumPost.objects.get(id=initial['parent_id'], forum=forum)
        except ForumPost.DoesNotExist:
            pass

    return render(request, 'core/create_forum_post.html', {
        'form': form,
        'forum': forum,
        'parent_post': parent_post,
    })

def forum_post_detail(request, forum_slug, post_id):
    forum = get_object_or_404(Forum, slug=forum_slug, is_hidden=False)
    post = get_object_or_404(ForumPost, id=post_id, forum=forum, is_hidden=False)
    replies = post.replies.filter(is_hidden=False).order_by('created_at')
    logger.info(f"Fetched {replies.count()} replies for post {post.id} in forum {forum.slug}")
    context = {
        'forum': forum,
        'post': post,
        'replies': replies,
    }
    return render(request, 'core/forum_post_detail.html', context)

def forum_post_replies(request, forum_slug, post_id):
    forum = get_object_or_404(Forum, slug=forum_slug, is_hidden=False)
    post = get_object_or_404(ForumPost, id=post_id, forum=forum, is_hidden=False)
    replies = post.replies.filter(is_hidden=False).order_by('created_at')
    context = {
        'forum': forum,
        'post': post,
        'replies': replies,
    }
    return render(request, 'core/forum_post_replies.html', context)

# Group views
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'core/group_list.html', {'groups': groups})

@login_required
def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public', 'on') == 'on'
        if Group.objects.filter(name=name).exists():
            return render(request, 'core/group_create.html', {'error': 'Group name already exists'})
        group = Group(name=name, description=description, creator=request.user, is_public=is_public)
        group.save()
        GroupMembership.objects.create(user=request.user, group=group, role='creator')
        return redirect('group_detail', group_id=group.id)
    return render(request, 'core/group_create.html')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    posts = Post.objects.filter(group=group, is_hidden=False).order_by('-created_at')
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    return render(request, 'core/group_detail.html', {'group': group, 'posts': posts, 'membership': membership})

@login_required
def group_join(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not GroupMembership.objects.filter(user=request.user, group=group).exists():
        GroupMembership.objects.create(user=request.user, group=group, role='member')
    return redirect('group_detail', group_id=group_id)

@login_required
def group_leave(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    if membership and membership.role != 'creator':
        membership.delete()
    return redirect('group_list')

@login_required
def group_moderate(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    if not membership or membership.role not in ['creator', 'moderator']:
        return redirect('group_detail', group_id=group_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_moderator':
            username = request.POST.get('username')
            user = User.objects.filter(username=username).first()
            if user and not GroupMembership.objects.filter(user=user, group=group).exists():
                GroupMembership.objects.create(user=user, group=group, role='moderator')
        elif action == 'remove_member':
            member_id = request.POST.get('member_id')
            member = GroupMembership.objects.filter(id=member_id, group=group).first()
            if member and member.role != 'creator':
                member.delete()
    members = GroupMembership.objects.filter(group=group)
    return render(request, 'core/group_moderate.html', {'group': group, 'members': members})

@login_required
def group_post(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    if not membership:
        return redirect('group_detail', group_id=group_id)
    return render(request, 'core/upload.html', {'type': request.GET.get('type', 'text'), 'group': group})

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'file', 'video_url', 'created_at', 'user']

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(post_type='video', is_hidden=False)
    serializer_class = VideoSerializer