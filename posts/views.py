from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.contrib.auth.decorators import login_required

def post_list(request):
    """게시글 목록"""
    posts = Post.objects.all().order_by("-created_at")  # 최신 글 순 정렬
    return render(request, "posts/post_list.html", {"posts": posts})

def post_detail(request, post_id):
    """게시글 상세 보기"""
    post = get_object_or_404(Post, id=post_id)
    return render(request, "posts/post_detail.html", {"post": post})

@login_required
def post_create(request):
    """게시글 작성"""
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        Post.objects.create(title=title, content=content, author=request.user)
        return redirect("post_list")

    return render(request, "posts/post_form.html")

@login_required
def post_update(request, post_id):
    """게시글 수정"""
    post = get_object_or_404(Post, id=post_id, author=request.user)  # 작성자만 수정 가능
    if request.method == "POST":
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        post.save()
        return redirect("post_detail", post_id=post.id)

    return render(request, "posts/post_form.html", {"post": post})

@login_required
def post_delete(request, post_id):
    """게시글 삭제"""
    post = get_object_or_404(Post, id=post_id, author=request.user)  # 작성자만 삭제 가능
    if request.method == "POST":
        post.delete()
        return redirect("post_list")

    return render(request, "posts/post_confirm_delete.html", {"post": post})
