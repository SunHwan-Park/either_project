from django import forms
from .models import Vote, Comment

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['title', 'description', 'category', 'item1', 'item2']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']