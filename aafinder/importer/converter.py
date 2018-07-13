def normalize_children(el):
    """
    Given an xml element, loop through every child element and evaluate every
    tag so we can replace tags.

    """
    children = el.getchildren()
    # go through the children backwards so that when a node is removed
    # it does not cause iteration errors for going out of bounds.
    children.reverse()
    for child in children:
        new_child = replace_nodes(child)  # noqa


def replace_nodes(el):
    """
    if we have a rule for processing a tag, then run the appropriate
    ElementBase class to handle it.

    """
    if el.tag in ElementBase.get_elements():
        temp = ElementBase.fetch(el.tag)
        temp.process(el)
    return el


def replace_parent_with_children_nodes(el):
    """
    Takes an element and replaces the itself with it's children,
    if there are no children and no text then the element is removed.
    """
    text = el.text or ''
    if len(el.getchildren()) == 0 and len(text.strip()) == 0:
        parent = el.getparent()
        parent.remove(el)
    else:
        normalize_children(el)
        parent = el.getparent()
        children = el.getchildren()
        index = parent.index(el)

        for child in children:
            parent.insert(index, child)
        parent.remove(el)


def get_flattened_text(el):
    """
    Returns the text contents of an element.
    """
    els = list(el.iter())
    out = []
    for e in els:
        if e.text is not None:
            out.append(e.text)
        if e.tail is not None:
            out.append(e.tail)

    return ''.join(out)


def remove_element(el, with_tail=False):
    """Remove an element, if with_tail is true
    do not preserve the tail of the element
    """
    parent = el.getparent()
    if el.tail:
        if parent.text:
            parent.text += el.tail
        else:
            parent.text = el.tail
    parent.remove(el)


class ElementBaseMetaClass(type):
    """
    Base class which allows XML tags to be registered and then processed on a
    tag by tag basis.

    """
    tag = None

    def __init__(self, class_name, bases, namespace):
        if not hasattr(self, 'element_types'):
            self.element_types = {}
        else:
            self.element_types[self.tag] = self

    def __str__(self):  # pragma: no cover
        return self.__name__

    def fetch(self, key):
        if key in self.element_types:
            return self.element_types[key]()
        else:  # pragma: no cover
            return None

    def get_elements(self, *args, **kwargs):
        """Returns a list ordered by the class name"""
        return self.element_types


# Both Python 2 and Python 3 compatiable
ElementBase = ElementBaseMetaClass('ElementBase', (object, ), {})


class Body(ElementBase):
    tag = "body"

    def process(self, el):
        normalize_children(el)


class Table(ElementBase):
    tag = "table"

    def process(self, el):
        normalize_children(el)


class Td(ElementBase):
    tag = "td"

    def process(self, el):
        normalize_children(el)


class Tr(ElementBase):
    tag = 'tr'

    def process(self, el):
        normalize_children(el)


class Th(ElementBase):
    tag = "th"

    def process(self, el):
        normalize_children(el)


class Font(ElementBase):
    tag = "font"

    def process(self, el):
        parent = el.getparent()
        if parent.text:
            parent.text += get_flattened_text(el)
        else:
            parent.text = get_flattened_text(el)
        parent.remove(el)


class Script(ElementBase):
    tag = "script"

    def process(self, el):
        parent = el.getparent()
        parent.remove(el)


class Style(ElementBase):
    tag = "style"

    def process(self, el):
        parent = el.getparent()
        parent.remove(el)

