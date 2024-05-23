#querying using db models Q
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.http import Http404



#caching imports
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from rest_framework.exceptions import PermissionDenied
#end caching imports

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from blango_auth.models import User

from blog.api.serializers import (
    PostSerializer,
    UserSerializer,
    PostDetailSerializer,
    TagSerializer,
)
from blog.models import Post, Tag

from blog.api.permissions import AuthorModifyOrReadOnly, IsAdminUserForObject

""" 
class PostList(generics.ListCreateAPIView):
  queryset = Post.objects.all()
  serializer_class = PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
  permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
  queryset = Post.objects.all()
  serializer_class = PostDetailSerializer

"""
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [AuthorModifyOrReadOnly | IsAdminUserForObject]
    queryset = Post.objects.all()


    #user based filtering

    def get_queryset(self):
        if self.request.user.is_anonymous:
            # published only
            queryset = self.queryset.filter(published_at__lte=timezone.now())

        elif not self.request.user.is_staff:
            # allow all
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(
                Q(published_at__lte=timezone.now()) | Q(author=self.request.user)
            )

        time_period_name = self.kwargs.get("period_name")

        if not time_period_name:
            # no further filtering required
            return queryset

        if time_period_name == "new":
            return queryset.filter(
                published_at__gte=timezone.now() - timedelta(hours=1)
            )
        elif time_period_name == "today":
            return queryset.filter(
                published_at__date=timezone.now().date(),
            )
        elif time_period_name == "week":
            return queryset.filter(published_at__gte=timezone.now() - timedelta(days=7))
        else:
            raise Http404(
                f"Time period {time_period_name} is not valid, should be "
                f"'new', 'today' or 'week'"
            )

#end user filtering

#serializer

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return PostSerializer
        return PostDetailSerializer

#caching function starts here#

    @method_decorator(cache_page(300))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    @action(methods=["get"], detail=False, name="Posts by the logged in user")
    def mine(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied("You must be logged in to see which Posts are yours")
        posts = self.get_queryset().filter(author=request.user)
        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

#We also want to cache the list of Posts for two 
# minutes, which means overriding the list() view. Implement this list() #
    @method_decorator(cache_page(120))
    def list(self, *args, **kwargs):
        return super(PostViewSet, self).list(*args, **kwargs)

#--caching ends--#


class UserDetail(generics.RetrieveAPIView):
  lookup_field = "email"
  queryset = User.objects.all()
  serializer_class = UserSerializer



#caching function starts here#
  ##Since this is a view, and not a viewset, we want to override and cache on the view methods.
  @method_decorator(cache_page(300))
  def get(self, *args, **kwargs):
    return super(UserDetail, self).get(*args, *kwargs)


#--caching ends--#



class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(methods=["get"], detail=True, name="Posts with the Tag")
    def posts(self, request, pk=None):
        tag = self.get_object()
        post_serializer = PostSerializer(
            tag.posts, many=True, context={"request": request}
        )
        return Response(post_serializer.data)

#caching function starts here#
#We’ll add caching to both the list() and retrieve() methods. #

    @method_decorator(cache_page(300))
    def list(self, *args, **kwargs):
        return super(TagViewSet, self).list(*args, **kwargs)

    @method_decorator(cache_page(300))
    def retrieve(self, *args, **kwargs):
        return super(TagViewSet, self).retrieve(*args, **kwargs)


#--caching ends--#

"""
https://arieldomino-jargontarget-8000.codio.io/api/v1/tags/1/
"""