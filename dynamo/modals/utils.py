"""
Used for lookups of related field values dynamically
https://stackoverflow.com/questions/20235807/how-to-get-foreign-key-values-with-getattr-from-models
"""


def get_repr(value):
    if callable(value):
        return '%s' % value()
    return value


def get_field(instance, field):
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem)
        except AttributeError:
            return None
    return attr
