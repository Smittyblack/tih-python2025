import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserRegisterForm
from .models import FriendRequest, Message, Profile, Notification
from django.contrib.auth.models import User
from core.models import Post, Comment
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    notification = Notification.objects.create(
        user=to_user,
        message=f"{request.user.username} sent you a friend request",
        link=reverse('user_profile', args=[request.user.username])
    )
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{to_user.id}',
        {
            'type': 'send_notification',
            'message': notification.message,
            'link': notification.link,
            'created_at': notification.created_at.isoformat(),
        }
    )
    return redirect('home')


@login_required
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        friend_request.accepted = True
        friend_request.save()
    return redirect('home')


@login_required
def reject_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        friend_request.delete()
    return redirect('home')


@login_required
def notifications(request):
    try:
        # Get full queryset for unread count and updates
        all_notifications = Notification.objects.filter(user=request.user)
        unread_count = all_notifications.filter(is_read=False).count()

        # Slice for top 10 newest notifications
        notifications = all_notifications.order_by('-created_at')[:10]
        logger.info(
            f"Fetching notifications for {request.user.username}: {notifications.count()} found (total: {all_notifications.count()})")

        if request.method == 'POST' and 'mark_read' in request.POST:
            all_notifications.update(is_read=True)  # Update full set
            logger.info("Marked notifications as read")
            return JsonResponse({'success': True})
        elif request.method == 'GET':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                all_notifications.update(is_read=True)  # Update full set
                notification_data = [{
                    'message': n.message,
                    'link': n.link,
                    'created_at': n.created_at.isoformat()
                } for n in notifications]
                logger.info(f"Returning JSON: {notification_data}")
                return JsonResponse({'notifications': notification_data})
            else:
                all_notifications.update(is_read=True)  # Update full set
                unread_count = 0
                return render(request, 'users/notifications.html', {
                    'notifications': notifications,
                    'unread_count': unread_count,
                })
    except Exception as e:
        logger.error(f"Error in notifications view: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def send_message(request, user_id):
    if request.method == 'POST':
        content = request.POST['core']
        receiver = User.objects.get(id=user_id)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('view_messages', user_id=user_id)
    return render(request, 'users/send_message.html', {'receiver_id': user_id})


@login_required
def view_messages(request, user_id):
    messages = Message.objects.filter(sender=request.user, receiver_id=user_id) | \
               Message.objects.filter(sender_id=user_id, receiver=request.user)
    messages = messages.order_by('timestamp')
    return render(request, 'users/view_messages.html', {'messages': messages, 'correspondent_id': user_id})


@login_required
def users_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'users/users_list.html', {'users': users})


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    # Check if the user is authenticated and has a moderator/admin role
    is_moderator_or_admin = request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.group in ['moderator', 'admin']
    
    hidden_posts = profile_user.post_set.filter(is_hidden=True) if is_moderator_or_admin else []
    hidden_comments = profile_user.comment_set.filter(is_hidden=True) if is_moderator_or_admin else []
    
    image_posts = profile_user.post_set.filter(post_type='image', is_hidden=False)
    video_posts = profile_user.post_set.filter(post_type='video', is_hidden=False)
    audio_posts = profile_user.post_set.filter(post_type='audio', is_hidden=False)
    text_link_posts = profile_user.post_set.filter(post_type__in=['text', 'link'], is_hidden=False)
    comments = profile_user.comment_set.filter(is_hidden=False)

    context = {
        'profile_user': profile_user,
        'hidden_posts': hidden_posts,
        'hidden_comments': hidden_comments,
        'image_posts': image_posts,
        'video_posts': video_posts,
        'audio_posts': audio_posts,
        'text_link_posts': text_link_posts,
        'comments': comments,
    }

    return render(request, 'users/userprofiles.html', context)


@login_required
def user_settings(request):
    return render(request, 'users/usersettings.html')