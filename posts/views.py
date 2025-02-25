from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, LikeDislike
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

def post_list(request):
    """게시글 목록"""
    posts = Post.objects.all().order_by("-created_at")  # 최신 글 순 정렬
    return render(request, "posts/post_list.html", {"posts": posts})

def post_detail(request, post_id):
    """게시글 상세 페이지 + 좋아요/싫어요 개수 포함"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    # 게시글 좋아요/싫어요 개수 계산
    post_likes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Post), object_id=post.id, value=1).count()
    post_dislikes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Post), object_id=post.id, value=-1).count()

    # 댓글별 좋아요/싫어요 개수 계산
    comment_reactions = {}
    for comment in comments:
        likes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Comment), object_id=comment.id, value=1).count()
        dislikes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Comment), object_id=comment.id, value=-1).count()
        comment_reactions[comment.id] = {"likes": likes, "dislikes": dislikes}

    return render(request, "posts/post_detail.html", {
        "post": post,
        "comments": comments,
        "post_likes": post_likes,
        "post_dislikes": post_dislikes,
        "comment_reactions": comment_reactions,
    })

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


@login_required
def like_dislike_post(request, post_id):
    """게시글 좋아요/싫어요 기능 (GenericForeignKey 기반)"""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    content_type = ContentType.objects.get_for_model(Post)  # 게시글 ContentType 가져오기

    if request.method == "POST":
        value = int(request.POST.get("value"))  # 1: 좋아요, -1: 싫어요
        existing_reaction = LikeDislike.objects.filter(
            content_type=content_type, object_id=post.id, user=user
        ).first()

        if existing_reaction:
            if existing_reaction.value == value:
                existing_reaction.delete()  # 동일한 반응이면 취소
            else:
                existing_reaction.value = value  # 다른 반응으로 변경
                existing_reaction.save()
        else:
            LikeDislike.objects.create(content_type=content_type, object_id=post.id, user=user, value=value)

    return redirect("post_detail", post_id=post.id)


@login_required
def like_dislike_comment(request, comment_id):
    """댓글 좋아요/싫어요 기능 (GenericForeignKey 기반)"""
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    content_type = ContentType.objects.get_for_model(Comment)  # 댓글 ContentType 가져오기

    if request.method == "POST":
        value = int(request.POST.get("value"))
        existing_reaction = LikeDislike.objects.filter(
            content_type=content_type, object_id=comment.id, user=user
        ).first()

        if existing_reaction:
            if existing_reaction.value == value:
                existing_reaction.delete()
            else:
                existing_reaction.value = value
                existing_reaction.save()
        else:
            LikeDislike.objects.create(content_type=content_type, object_id=comment.id, user=user, value=value)

    return redirect("post_detail", post_id=comment.post.id)
    
    
    
@login_required
def add_comment(request, post_id):
    """댓글 추가 기능"""
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
    
    return redirect("post_detail", post_id=post.id)  # 댓글 작성 후 게시글 상세 페이지로 리디렉트