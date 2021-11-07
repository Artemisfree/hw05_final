from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm

from .models import Comment, Follow, Group, Post, User


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'title_index': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile(request, username):
    template = 'posts/profile.html'
    user = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=user, author=author).exists()
    posts = Post.objects.filter(author=author)
    counter = posts.count()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': posts,
        'counter': counter,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    post_text = post.text[:30]
    author = post.author
    counter = Post.objects.filter(author=author).count()
    comments = Comment.objects.filter(post=post)
    comment_form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_text': post_text,
        'counter': counter,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            'posts:profile', username=request.user
        )
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    groups = Group.objects.all()
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    # form = PostForm(instance=post)
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
        'groups': groups,
    }
    return render(request, template, context)


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
    template = 'posts/follow.html'
    title = 'Мои подписки'
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts = Post.objects.filter(author__in=authors)
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'posts': posts,
        'title': title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    print(user)
    author = get_object_or_404(User, username=username)
    Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=request.user)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=request.user)
