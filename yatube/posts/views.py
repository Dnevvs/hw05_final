from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from .forms import PostForm, CommentForm
from .models import Comment, Follow, Group, Post, User
from .utils import mypaginator


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('group')
    page_obj = mypaginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group').filter(group=group)
    page_obj = mypaginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('group').filter(author=author)
    post_count = post_list.count()
    page_obj = mypaginator(request, post_list)
    following = False
    if request.user.is_authenticated:
        follow_list = Follow.objects.select_related(
            'user', 'author').filter(user=request.user).filter(author=author)
        if follow_list:
            following = True
    context = {
        'page_obj': page_obj,
        'author': author,
        'post_count': post_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comment_list = Comment.objects.select_related('post').filter(post=post)
    context = {
        'comments': comment_list,
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'post_id': post_id, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_list = Follow.objects.select_related(
        'user', 'author').filter(user=request.user)
    author_list = [f.author for f in follow_list]
    post_list = Post.objects.select_related(
        'author').filter(author__in=author_list)
    page_obj = mypaginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follows = Follow.objects.select_related(
        'user').filter(author=author)
    if request.user != author and len(follows) < 1:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, author=author)
    follow.delete()
    return redirect('posts:profile', author)
