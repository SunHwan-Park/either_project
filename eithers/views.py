from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import VoteForm, CommentForm
from .models import Vote, VoteSelection, Comment
from django.contrib import messages

# Create your views here.
def index(request):
    votes = Vote.objects.all()
    context = {
        'votes': votes,
    }
    return render(request, 'eithers/vote_list.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.creator = request.user
            vote.save()
            messages.info(request, '질문이 생성되었습니다.')
            return redirect('eithers:detail', vote.pk)
    else:
        form = VoteForm()
    context = {
        'form':form,
    }
    return render(request, 'eithers/form.html', context)

@login_required
def detail(request, vote_pk):
    vote = get_object_or_404(Vote, pk=vote_pk)
    comment_form = CommentForm()
    try:
        selection = get_object_or_404(VoteSelection, user=request.user, vote=vote)
        context = {
            'vote': vote,
            'comment_form': comment_form,
            'selection': selection,
        }
    except:
        context = {
            'vote': vote,
            'comment_form': comment_form,
            'selection': [],
        }
    return render(request, 'eithers/vote_detail.html', context)

@require_POST
@login_required
def selectitem(request, vote_pk):
    vote = get_object_or_404(Vote, pk=vote_pk)
    vs = VoteSelection()
    vs.vote = vote
    vs.user = request.user
    if 'item1' in request.POST:
        vs.selection = 1
        vote.item1_num += 1
    elif 'item2' in request.POST:
        vs.selection = 2
        vote.item2_num += 1
    vs.save()
    vote.save()
    messages.info(request, '투표에 성공하셨습니다!')
    return redirect('eithers:detail', vote.pk)

@login_required
def comment_create(request, vote_pk):
    vote = get_object_or_404(Vote, pk=vote_pk)
    try:
        selection = get_object_or_404(VoteSelection, user=request.user, vote=vote)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.vote = vote
            comment.selection = selection
            comment.save()
            messages.info(request, '댓글이 생성되었습니다.')
    except:
        messages.info(request, '투표를 먼저 진행해주세요.')
    return redirect('eithers:detail', vote.pk)
