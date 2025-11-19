# internethub/tv/views.py
from django.shortcuts import render
from core.models import Post  # Import from core
from rest_framework import viewsets
from rest_framework import serializers

def tv_home(request):
    videos = Post.objects.filter(post_type='video', is_hidden=False).order_by('-created_at')
    return render(request, 'tv/home.html', {'videos': videos})

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'file', 'video_url', 'created_at', 'user']

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(post_type='video', is_hidden=False)
    serializer_class = VideoSerializer