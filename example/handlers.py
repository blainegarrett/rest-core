"""
Example Handlers for the Blog Posts

Note: This does not deal with any sort of permissions - not production friendly
"""

import voluptuous

from rest_core.handlers import RestHandlerBase
from rest_core.resources import Resource
from rest_core.resources import RestField, SlugField, ResourceIdField
from rest_core.resources import ResourceUrlField, DatetimeField, BooleanField
from rest_core.params import coerce_to_datetime
from rest_core.params import coerce_to_cursor

from example import api as posts_api
from example.utils import get_domain
from example.models import BlogPost


# Resource Setup
resource_url = 'http://' + get_domain() + '/posts/%s'  # TODO: Define this differently

BLOG_POST_REST_RULES = [
    ResourceIdField(output_only=True),
    ResourceUrlField(resource_url, output_only=True),
    SlugField(BlogPost.slug, required=True),
    RestField(BlogPost.title, required=True),
    RestField(BlogPost.permalink, output_only=True),

    RestField(BlogPost.content),
    RestField(BlogPost.summary),

    DatetimeField(BlogPost.created_date, output_only=True),
    DatetimeField(BlogPost.modified_date, output_only=True),
    DatetimeField(BlogPost.published_date, required=False),
    BooleanField(BlogPost.is_published),
]


class PostsApiHandler(RestHandlerBase):
    """
    Blog Posts Collection REST Endpoint
    """

    def get_param_schema(self):
        """
        Get set of allowed params and their validators
        """

        return {
            u'limit': voluptuous.Coerce(int),
            u'cursor': coerce_to_cursor,
            u'get_by_slug': voluptuous.Coerce(unicode),
            u'is_published': voluptuous.Coerce(voluptuous.Boolean()),
            u'start_date': coerce_to_datetime
        }

    def get_rules(self):
        return BLOG_POST_REST_RULES

    def _get_by_slug_or_404(self, slug):
        """
        Given a slug, attempt to return slug resource or issue a 404
        """

        post = posts_api.get_post_by_slug(slug)

        if not post:
            self.serve_404('Resource given by slug %s Not Found' % slug)
            return

        # Found Post: Serve it up
        self.serve_success(Resource(post, BLOG_POST_REST_RULES).to_dict())
        return

    def _get(self):
        """
        Get a collection of Blog Posts or query for specific criteria
        """

        # Check if we want to get a post by its slug
        get_by_slug = self.cleaned_params.get('get_by_slug', None)

        if get_by_slug:
            return self._get_by_slug_or_404(get_by_slug)

        # Get a list of all posts
        limit = self.cleaned_params.get('limit', None)
        cursor = self.cleaned_params.get('cursor', None)
        start_date = self.cleaned_params.get('start_date', None)

        optional_params = {}
        if 'is_published' in self.params:
            optional_params['is_published'] = self.cleaned_params['is_published']

        if start_date:
            optional_params['start_date'] = start_date

        # TODO: Leverage request key to leverage memcache for return hits
        entities, cursor, more = posts_api.get_posts(limit=limit, cursor=cursor,
                                                     **optional_params)

        # Create A set of results based upon this result set - iterator??
        results = []
        for e in entities:
            results.append(Resource(e, BLOG_POST_REST_RULES).to_dict())

        if cursor:
            cursor = cursor.urlsafe()

        self.serve_success(results, {'cursor': cursor, 'more': more})

    def _post(self):
        """
        Create a Post
        """

        post = posts_api.create_post(self.cleaned_data)
        self.serve_success(Resource(post, BLOG_POST_REST_RULES).to_dict())


class PostDetailApiHandler(RestHandlerBase):
    """
    Blog Post Resource Endpoint
    """

    def get_rules(self):
        return BLOG_POST_REST_RULES

    def _get(self, resource_id):
        """
        Get a post by resource id
        Note: To get a post by slug id, hit collection endpoint (/?get_by_slug=slug)
        """

        post = posts_api.get_post_by_resource_id(resource_id)
        self.serve_success(Resource(post, BLOG_POST_REST_RULES).to_dict())

    def _put(self, resource_id):
        """
        Edit a Post given by resource_id
        """

        # First retrieve the post to edit
        post = posts_api.get_post_by_resource_id(resource_id)
        if not post:
            return self.serve_404('Resource given by resource id %s Not Found' % resource_id)

        post = posts_api.edit_post(post, self.cleaned_data)

        self.serve_success(Resource(post, BLOG_POST_REST_RULES).to_dict())
