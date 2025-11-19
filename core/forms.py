import mimetypes
import magic
from django import forms
from .models import Post, Comment, ImageAttachment

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'id': 'id_content'}), required=False)
    video_file = forms.FileField(required=False)  # For video tab
    audio_file = forms.FileField(required=False)  # For audio tab
    url = forms.URLField(required=False)  # For link tab
    video_url = forms.URLField(required=False)  # For YouTube URL in video tab
    description = forms.CharField(widget=forms.Textarea(attrs={'id': 'id_description'}), required=False)  # For video/link descriptions

    class Meta:
        model = Post
        fields = ['post_type', 'title', 'content', 'file', 'thumbnail', 'link', 'video_url']
        widgets = {
            'post_type': forms.Select(attrs={'id': 'post-type-select'}),
            'file': forms.FileInput(attrs={'id': 'id_file'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        post_type = cleaned_data.get('post_type')
        video_file = self.files.get('video_file') if 'video_file' in self.files else None
        audio_file = self.files.get('audio_file') if 'audio_file' in self.files else None
        url = cleaned_data.get('url')
        video_url = cleaned_data.get('video_url')

        if post_type == 'text':
            if video_file or audio_file:
                raise forms.ValidationError("Text posts should not include files.")
        elif post_type == 'image':
            # Validation moved to view since we're handling multiple files directly
            pass
        elif post_type == 'video':
            if (video_file and video_url) or (not video_file and not video_url):
                raise forms.ValidationError("Choose either a video file upload or a YouTube URL, not both.")
            if video_file:
                mime_type_guess, _ = mimetypes.guess_type(video_file.name)
                if not mime_type_guess:
                    mime_type_guess = 'unknown'
                mime_type_actual = magic.from_buffer(video_file.read(1024), mime=True)
                video_file.seek(0)
                allowed_mime_types = ['video/mp4', 'video/x-msvideo', 'video/quicktime']
                if mime_type_guess not in allowed_mime_types:
                    raise forms.ValidationError(f"Invalid file type (guessed: {mime_type_guess}) for video post.")
                if mime_type_actual not in allowed_mime_types:
                    raise forms.ValidationError(f"Invalid file content (actual: {mime_type_actual}) for video post.")
        elif post_type == 'audio':
            if not audio_file:
                raise forms.ValidationError("An audio file is required for audio posts.")
            mime_type_guess, _ = mimetypes.guess_type(audio_file.name)
            if not mime_type_guess:
                mime_type_guess = 'unknown'
            mime_type_actual = magic.from_buffer(audio_file.read(1024), mime=True)
            audio_file.seek(0)
            allowed_mime_types = ['audio/mpeg', 'audio/wav', 'audio/ogg']
            if mime_type_guess not in allowed_mime_types:
                raise forms.ValidationError(f"Invalid file type (guessed: {mime_type_guess}) for audio post.")
            if mime_type_actual not in allowed_mime_types:
                raise forms.ValidationError(f"Invalid file content (actual: {mime_type_actual}) for audio post.")
        elif post_type == 'link':
            if not url:
                raise forms.ValidationError("A URL is required for link posts.")

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'id': 'id_comment_content'}),
        }