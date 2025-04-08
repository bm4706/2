from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, LikeDislike, Bookmark
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from django.db.models import Q
from .forms import CommentForm, PostSearchForm, PostForm

from users.models import Follow

from notifications.utils import create_notification
from notifications.models import Notification

def post_list(request):
    """게시글 목록 + 검색 기능"""
    # 검색 폼 처리
    form = PostSearchForm(request.GET)
    posts = Post.objects.all().order_by("-created_at")  # 기본: 최신 글 순
    
    # 검색 처리
    if form.is_valid() and 'query' in request.GET:
        query = form.cleaned_data['query']
        search_type = form.cleaned_data['search_type']
        
        if query:  # 검색어가 있는 경우만 필터링
            if search_type == 'title':
                posts = posts.filter(title__icontains=query)
            elif search_type == 'content':
                posts = posts.filter(content__icontains=query)
            elif search_type == 'author':
                posts = posts.filter(author__nickname__icontains=query)
            else:  # 'all' 또는 기타 경우
                posts = posts.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(author__nickname__icontains=query)
                )
    
    context = {
        'posts': posts,
        'form': form,
        'query': request.GET.get('query', ''),
        'search_type': request.GET.get('search_type', 'all'),
    }
    
    return render(request, "posts/post_list.html", context)
def post_detail(request, post_id):
    """게시글 상세 페이지 + 좋아요/싫어요 개수 포함"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent=None)  # 부모 댓글만 가져오기
    comment_form = CommentForm()  # 댓글 폼 추가

    # 게시글 좋아요/싫어요 개수 계산
    post_likes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Post), object_id=post.id, value=1).count()
    post_dislikes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Post), object_id=post.id, value=-1).count()

    # 댓글별 좋아요/싫어요 개수 계산
    comment_reactions = {}
    for comment in post.comments.all():
        likes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Comment), object_id=comment.id, value=1).count()
        dislikes = LikeDislike.objects.filter(content_type=ContentType.objects.get_for_model(Comment), object_id=comment.id, value=-1).count()
        comment_reactions[comment.id] = {"likes": likes, "dislikes": dislikes}

    # 현재 사용자가 게시글 작성자를 팔로우하고 있는지 확인
    is_following = False
    if request.user.is_authenticated and request.user != post.author:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=post.author
        ).exists()   
    
    
    return render(request, "posts/post_detail.html", {
        "post": post,
        "comments": comments,
        "post_likes": post_likes,
        "post_dislikes": post_dislikes,
        "comment_reactions": comment_reactions,
        "is_followings": is_following,
        "comment_form": comment_form,
    })

@login_required
def post_create(request):
    """게시글 작성"""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)  # request.FILES 추가
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm()

    return render(request, "posts/post_form.html", {"form": form})

@login_required
def post_update(request, post_id):
    """게시글 수정"""
    post = get_object_or_404(Post, id=post_id, author=request.user)  # 작성자만 수정 가능
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)  # request.FILES 추가
        if form.is_valid():
            form.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "posts/post_form.html", {"form": form, "post": post})

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
    """
    댓글 추가 기능
    - parent_id가 있으면 대댓글 추가
    - 없으면 일반 댓글 추가
    """
    post = get_object_or_404(Post, id=post_id)
    parent_id = request.POST.get('parent_id')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # 대댓글인 경우 부모 댓글 설정
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment
                comment.save()
                
                # 대댓글 알림 생성
                create_notification(
                    recipient=parent_comment.author,
                    actor=request.user,
                    notification_type=Notification.REPLY,
                    content_object=comment
                )
            else:
                comment.save()
                
                # 일반 댓글 알림 생성
                create_notification(
                    recipient=post.author,
                    actor=request.user,
                    notification_type=Notification.COMMENT,
                    content_object=comment
                )
            
            messages.success(request, "댓글이 등록되었습니다.")  # 피드백 추가
    
    return redirect("post_detail", post_id=post.id)



@login_required
def bookmark_toggle(request, post_id):
    """북마크 추가/제거 토글 기능"""
    post = get_object_or_404(Post, id=post_id)
    
    # 이미 북마크했는지 확인
    bookmark = Bookmark.objects.filter(user=request.user, post=post)
    
    if bookmark.exists():
        # 이미 북마크가 있으면 제거
        bookmark.delete()
        messages.success(request, "북마크가 제거되었습니다.")
    else:
        # 북마크가 없으면 추가
        Bookmark.objects.create(user=request.user, post=post)
        messages.success(request, "북마크에 추가되었습니다.")
    
    # 이전 페이지로 리디렉션 (HTTP_REFERER가 있으면 사용, 없으면 post_detail로)
    if 'HTTP_REFERER' in request.META:
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('post_detail', post_id=post_id)

@login_required
def bookmark_list(request):
    """사용자의 북마크 목록 보기"""
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
    bookmarked_posts = [bookmark.post for bookmark in bookmarks]
    
    return render(request, "posts/bookmark_list.html", {"bookmarked_posts": bookmarked_posts})





def tag_posts(request, tag_name):
    """특정 태그가 있는 게시글만 보기"""
    posts = Post.objects.filter(tags__name__in=[tag_name]).order_by('-created_at')
    
    return render(request, 'posts/tag_posts.html', {
        'tag_name': tag_name,
        'posts': posts
    })