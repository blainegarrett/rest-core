from google.appengine.ext import ndb
from example.utils import get_domain


class BlogPost(ndb.Model):
    """
    Model for Blog Post
    """

    title = ndb.StringProperty()  # Post Name
    slug = ndb.StringProperty()  # Post slug for permalinks
    content = ndb.TextProperty()
    summary = ndb.TextProperty()

    created_date = ndb.DateTimeProperty(auto_now_add=True)
    modified_date = ndb.DateTimeProperty(auto_now=True)
    published_date = ndb.DateTimeProperty(indexed=True)
    is_published = ndb.BooleanProperty(default=False, indexed=True)

    @property
    def permalink(self):
        """
        Generate an relative url for the permalink
        """
        # TODO: what to return if not published...

        pub_date = self.published_date
        args = (pub_date.year, str(pub_date.month).zfill(2), self.slug)
        return '/written/%s/%s/%s/' % args

    @property
    def absolute_permalink(self):
        """
        Generate an absolute url for the permalink
        """
        return 'http://%s%s' % (get_domain(), self.permalink)
