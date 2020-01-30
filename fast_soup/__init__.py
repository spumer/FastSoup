"""Provide BeautifulSoup-like interface object
to fast html parsing.

Interface more simple than original and don't allow use all features.
"""

import functools
import io

import lxml.etree
import lxml.html
from bs4 import SoupStrainer as BS4SoupStrainer

try:
    import lxml.cssselect

    xml_translator = lxml.cssselect.LxmlTranslator()
    html_translator = lxml.cssselect.LxmlHTMLTranslator()

except ImportError as exc:

    class RaiseOnUse:
        def __init__(self, e):
            self.exc = e

        def __getattr__(self, item):
            raise self.exc

    xml_translator = RaiseOnUse(exc)
    html_translator = RaiseOnUse(exc)


__version__ = '1.0.0'

_missing = object()


def _el2str(el):
    return lxml.etree.tostring(el, method='c14n', with_tail=False).decode()


def _parse_html(html, parser=lxml.html.html_parser):
    return lxml.etree.parse(io.StringIO(html), parser=parser)


class HDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class Tag:
    scope_rel = '.'

    __slots__ = ('_el', '_translator')

    def __init__(self, el):
        if isinstance(el, lxml.html.HtmlElement):
            translator = html_translator
        else:
            translator = xml_translator

        self._el = el
        self._translator = translator

    def unwrap(self):
        return self._el

    def get_text(self, separator='', strip=False):
        return separator.join(x.strip() if strip else x for x in self._el.itertext())  # noqa: IF100

    def __str__(self):
        return _el2str(self._el)

    def clear(self):
        return self._el.clear()

    def get(self, item, default=None):
        return self._el.get(item, default)

    def __getitem__(self, item):
        value = self.get(item, _missing)
        if value is _missing:
            raise KeyError(item)
        return value

    def select(self, selector):
        xpath = self._build_css_xpath(selector, self._translator)
        return xpath(self._el)

    @property
    def name(self):
        return self._el.tag

    @name.setter
    def name(self, value):
        self._el.tag = value

    @property
    def string(self):
        return self._el.text

    @classmethod
    def _get_scope(cls, recursive=True):
        if recursive:
            return cls.scope_rel + '//'
        else:
            return cls.scope_rel + '/'

    @classmethod
    @functools.lru_cache()
    def _build_css_xpath(cls, selector, translator):
        return lxml.etree.XPath(translator.css_to_xpath(selector))

    @classmethod
    def _build_attrs_xpath(cls, attrs):
        attrs_xpath = []

        def _render(name, value, tmplt):
            return tmplt.format(name, value.replace('"', '\\"'),)

        for attr_name, attr_value in attrs.items():
            if attr_name == 'text':
                # for case: [text()="..."]
                attr_name = 'text()'
            else:
                # for case: [@id="..."]
                attr_name = '@' + attr_name

            if attr_value:
                # lxml is more strict than BS4
                # BS4 mean "contains" logic for attribute search
                # Use lxml `contains` function to implement this behaviour:
                # using the space delimiters to find the class name boundaries
                # cause `contains` match a substring
                tmplt = 'contains(concat(" ", normalize-space({}), " "), " {} ")'
                attr_xpath = _render(attr_name, attr_value, tmplt)

            # If attr value is empty guess should match tags without this attr too
            # cause BS4 do that
            else:
                # lxml don't match this case, workaround by inverse
                attr_xpath = 'not(%s)' % _render(attr_name, attr_value or '', '{} != "{}"')

            attrs_xpath.append(attr_xpath)

        return attrs_xpath

    @classmethod
    def _build_single_xpath(cls, name=None, attrs=None, _mode=None, _scope=None):
        """Build XPath by given attrs

        @param name: tag name
        @param attrs: tag attributes
        @param _mode: xpath search mode (e.g 'following', 'following-sibling')
        @return: str
        """
        scope = _scope

        if scope is None:
            scope = cls._get_scope()

        xpath = [scope]

        if name is None:
            name = '*'

        if _mode is not None:
            name = '%s::%s' % (_mode, name)

        xpath.append(name)

        if attrs:
            attrs_xpath = cls._build_attrs_xpath(attrs)
            xpath.append('[' + ' and '.join(attrs_xpath) + ']')

        return ''.join(xpath)

    @classmethod
    @functools.lru_cache()
    def _build_xpath(cls, names=(), attrs=None, _mode=None, _scope=None) -> lxml.etree.XPath:
        """Build XPath expression

        @param names: tags names
        @param attrs: tags attributes (applied for each tag)
        @return: compiled xpath expression
        """
        if not names:
            return lxml.etree.XPath(cls._build_single_xpath(None, attrs, _mode, _scope))

        return lxml.etree.XPath(' | '.join(cls._build_single_xpath(n, attrs, _mode, _scope) for n in names))

    def _find_all(self, name=None, attrs=None, _mode=None, _scope=None):
        if not isinstance(name, BS4SoupStrainer):
            _strainer = BS4SoupStrainer(name, **attrs)
        else:
            _strainer = name

        # гарантируем что name и attrs всегда будут иметь один формат
        name = _strainer.name
        attrs = _strainer.attrs

        if _strainer.text is not None:
            # don't override if `text` field was manually setted before
            attrs.setdefault('text', _strainer.text)

        if isinstance(name, list):
            # _build_xpath принимает только хэшируемые параметры
            names = tuple(name)
        else:
            names = (name,)

        xpath = self._build_xpath(names, HDict(attrs), _mode=_mode, _scope=_scope)
        return [Tag(el) for el in xpath(self._el)]

    def _find(self, name=None, attrs=None, _mode=None, _scope=None):
        res = self._find_all(name=name, attrs=attrs, _mode=_mode, _scope=_scope)

        if res:
            return res[0]

        return None

    def find_all(self, name=None, recursive=True, **attrs):
        scope = self._get_scope(recursive)
        return self._find_all(name, attrs, _scope=scope)

    def find(self, name=None, recursive=True, **attrs):
        scope = self._get_scope(recursive)
        return self._find(name, attrs, _scope=scope)

    def find_next(self, name=None, **attrs):
        return self._find(name, attrs, _mode='following')

    def find_next_sibling(self, name=None, **attrs):
        return self._find(name, attrs, _mode='following-sibling', _scope='./')


class FastSoup(Tag):
    scope_rel = ''

    def __init__(self, markup=''):
        tree = _parse_html(markup)
        super().__init__(el=tree.getroot())
