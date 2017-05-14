
# Base model class
# from google.appengine.ext import ndb

# TODO: Eventually re-work this so it doesn't extend ndb.Model


class Model():  # ndb.Model):
    id = None

    def get_kind(self):
        return self.__class__.__name__

    # Temp hack - hide the ndb data operations
    def put_multi_async(*args, **kwargs):
        raise Exception("Method not implemented...")

    def put_multi(*args, **kwargs):
        raise Exception("Method not implemented...")

    def get_multi_async(*args, **kwargs):
        raise Exception("Method not implemented...")

    def delete_multi_async(*args, **kwargs):
        raise Exception("Method not implemented...")

    def delete_multi(*args, **kwargs):
        raise Exception("Method not implemented...")

    def get_indexes_async(*args, **kwargs):
        raise Exception("Method not implemented...")

    def get_indexes(*args, **kwargs):
        raise Exception("Method not implemented...")

    def __repr__(self):
        """Return an unambiguous string representation of an entity."""
        # Modified from original appengine version to not deal with ndb.keys
        args = []
        for prop in self._properties.itervalues():
            if prop._has_value(self):
                val = prop._retrieve_value(self)
                if val is None:
                    rep = 'None'
                elif prop._repeated:
                    reprs = [prop._value_to_repr(v) for v in val]
                    if reprs:
                        reprs[0] = '[' + reprs[0]
                        reprs[-1] = reprs[-1] + ']'
                        rep = ', '.join(reprs)
                    else:
                        rep = '[]'
                else:
                    rep = prop._value_to_repr(val)
                args.append('%s=%s' % (prop._code_name, rep))
        args.sort()
        if self.id is not None:
            args.insert(0, 'id=%r' % self.id)
        if self._projection:
            args.append('_projection=%r' % (self._projection,))
        s = '%s(%s)' % (self.__class__.__name__, ', '.join(args))
        return s