"""
Example Internal API for Blog Posts

TODO: This is fairly spaghetti code and needs better error handling, etc.
TODO: Add delete
TODO: Add transaction for unique slug check
TODO: Leverage search api for filters to avoid Index bloat
TODO: Add doc strings and unit tests
"""

import datetime
from rest_core.utils import get_key_from_resource_id
from example.models import BlogPost
from example.constants import QUERY_LIMIT


def get_post_by_resource_id(resource_id):
    """
    Given a resource id, fetch the post entity

    TODO: Ensure that it is of kind BlogCategory and not some other Entity type
    """

    key = get_key_from_resource_id(resource_id)
    return key.get()


def get_posts(limit=QUERY_LIMIT, cursor=None, **kwargs):
    """
    Primary wrapper for fetching events
    """

    if not limit:
        limit = QUERY_LIMIT

    # Setup Base Query
    q = BlogPost.query()

    if 'is_published' in kwargs:
        q = q.filter(BlogPost.is_published == kwargs['is_published'])

    if 'start_date' in kwargs:
        q = q.filter(BlogPost.published_date >= kwargs['start_date'])

    q = q.order(-BlogPost.published_date)

    entites, cursor, more = q.fetch_page(limit, start_cursor=cursor)
    return entites, cursor, more


def get_post_by_slug(slug):
    """
    Simple Helper to fetch a post via slug.
    """

    entity = BlogPost.query(BlogPost.slug == slug).get()
    return entity


def create_post(data):
    """
    Create a blog post
    """

    # Step 1: Validate data - ensure slug is unique (TODO: Add transaction)
    v = BlogPost.query(BlogPost.slug == data['slug']).get()
    if v:
        err = 'There is already an Post with the slug "%s". Please select another.'
        raise Exception(err % data['slug'])

    # Step 2:  Create the base Post Model
    entity = BlogPost()

    maybe_publish = bool(data.get('is_published', False))

    if maybe_publish:
        entity.is_published = True  # Regardless of it it was already true

        if data.get('published_date'):
            entity.published_date = data.get('published_date').replace(tzinfo=None)
        elif entity.published_date is None:
            entity.published_date = datetime.datetime.now()  # TODO: Convert to CST
        # else: was previously published so leave the previously published date

    entity.slug = data.get('slug')  # required by the REST rules
    entity.title = data.get('title')  # required by REST rules
    entity.summary = data.get('summary')
    entity.content = data.get('content')
    entity.put()

    return entity


def edit_post(entity, data):
    """
    Edit an post
    """

    # Create the base Event Model
    maybe_publish = bool(data['is_published'])
    should_unpublish = (not bool(data['is_published'])) and bool(entity.published_date)

    if maybe_publish:
        entity.is_published = True  # Regardless of it it was already true

        if data.get('published_date'):
            entity.published_date = data['published_date'].replace(tzinfo=None)
        elif entity.published_date is None:
            entity.published_date = datetime.datetime.now()  # TODO: Convert to CST
        # else: was previously published so leave the previously published date

    if should_unpublish:
        # Let's mark as not published - but preserve original published date for archives
        entity.is_published = False

    entity.slug = data.get('slug')
    entity.title = data.get('title')
    entity.slug = data.get('slug')
    entity.title = data.get('title')
    entity.summary = data.get('summary')
    entity.content = data.get('content')

    entity.put()

    # Step 2: Next update the search indexes incase anything affecting them has changed
    # maybe_up_update_search_index(entity)

    # Step 3: Kill All caches
    return entity
