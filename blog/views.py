from django.utils import timezone
from blog.models import Post, Comment
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from blog.forms import CommentForm

# Create your views here.
def index(request):
    posts = Post.objects.filter(published_at__lte=timezone.now())
    ''' 
    DATABASE QUERY OPTIMISATION...USE ONLY IF A PERMANENT QUERY SET
    #.select_related("author")
    #.defer("created_at", "modified_at")
    #or the oppossite use 
    #.only("title", "summary", "content", "author", "published_at", "slug")
    '''

    return render(request, "blog/index.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user.is_active:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None

    #return render(request, "blog/post-detail.html", {"post": post})

    return render(request, "blog/post-detail.html", {"post": post, "comment_form": comment_form}
)

def get_ip(request):
  from django.http import HttpResponse
  return HttpResponse(request.META['REMOTE_ADDR'])

def post_table(request):
    return render(request, "blog/post-table.html")