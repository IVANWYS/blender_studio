from typing import List

from django.views.generic import ListView, DetailView
from django.db.models.query import QuerySet
from django.contrib.syndication.views import Feed
from django.utils import feedgenerator

from blog.models import Post, Like
from blog.queries import get_posts
from comments.models import Comment
from comments.queries import get_annotated_comments
from comments.views.common import comments_to_template_type


class PostList(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self) -> QuerySet:
        return get_posts(
            user_pk=self.request.user.pk if self.request.user.is_authenticated else None
        )


class PostDetail(DetailView):
    model = Post
    context_object_name = 'post'

    def get_object(self) -> Post:
        object_ = super().get_object()
        if self.request.user.is_authenticated:
            object_.liked = Like.objects.filter(
                post_id=object_.pk, user_id=self.request.user.pk
            ).exists()
        return object_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post: Post = self.get_object()
        # Display edit buttons for editors/authors
        context['user_can_edit_post'] = self.request.user.is_staff and self.request.user.has_perm(
            'blog.change_post'
        )

        if post.film and post.author.film_crew.filter(film=post.film):
            context['user_film_role'] = post.author.film_crew.filter(film=post.film)[0].role

        # Comment threads
        comments: List[Comment] = get_annotated_comments(post, self.request.user.pk)
        context['comments'] = comments_to_template_type(
            comments, post.comment_url, self.request.user
        )

        return context


class PostFeed(Feed):
    title = 'Blender Studio feed'
    link = '/blog/'
    description = 'Updates from Blender Studio'

    def item_enclosures(self, item: Post):
        return [
            feedgenerator.Enclosure(
                item.thumbnail_m_url,
                str(item.thumbnail.size),
                'image/{}'.format(item.thumbnail.name.split('.')[-1]),
            )
        ]

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-date_published')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt
