from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta


@login_required
def chat_room(request, room_name):

    # Search messages
    search_query = request.GET.get('search', '')

    # Username search
    username_search = request.GET.get("username_search", "")

    # Base user list
    users = User.objects.exclude(id=request.user.id)

    # Apply username filter
    if username_search:
        users = users.filter(username__icontains=username_search)

    # Chat messages
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(content__icontains=search_query)

    chats = chats.order_by('timestamp')

    # Last message list with online/offline status
    user_last_messages = []
    now = timezone.now()

    # ONLINE TIMEOUT = 2 minute
    ONLINE_TIMEOUT = timedelta(minutes=2)

    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        # Get last_seen safely
        last_seen = getattr(user.profile, "last_seen", None)

        # Check if user is online
        is_online = False
        if last_seen:
            is_online = (now - last_seen) < ONLINE_TIMEOUT

        user_last_messages.append({
            'user': user,
            'last_message': last_message,
            'is_online': is_online
        })

    # timezone fallback
    fallback_time = timezone.make_aware(datetime.min)

    # Sort list
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else fallback_time,
        reverse=True
    )

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'username_search': username_search,
    })


def search_users(request):
    query = request.GET.get("search", "")

    if query:
        filtered_users = User.objects.filter(username__icontains=query)
    else:
        filtered_users = User.objects.all()

    return render(request, "search_users.html", {
        "filtered_users": filtered_users,
    })
