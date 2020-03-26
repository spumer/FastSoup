import functools

import pytest
from bs4 import BeautifulSoup as BS4Soup

from fast_soup import FastSoup


@pytest.fixture()
def data():
    return '''
<html>

<a href="">   It's a text    </a>
<a>No href</a>

<div id="first">
    <p id="following"></p>
</div>

<p id="sibling">
</p>

<p id="multiline">
    Multiline
    <br/>
    text
</p>

<h1 class="multiple-value multiple-value2"></h1>
<h1 class="multiple-value-sub multiple-value2-sub"></h1>

<table class="recursive">
<tr>
    <td>
    <table><tr><td>Inner row</td></tr></table>
    </td>
</tr>
<tr>
    <td>
    Row
    </td>
</tr>
</table>

<div>
    <span class="body strikeout"></span>
</div>

</html>

    '''


@pytest.fixture(params=['bs4', 'fast-soup'])
def soup_cls(request):
    if request.param == 'bs4':
        return functools.partial(BS4Soup, features='lxml')
    else:
        assert request.param == 'fast-soup'
        return FastSoup


@pytest.fixture()
def soup(soup_cls, data):
    return soup_cls(data)


def test_common(soup):
    res = soup.find('a')

    assert res.name == 'a'

    assert res.get_text() == '   It\'s a text    '
    assert res.get_text(strip=True) == 'It\'s a text'

    res = soup.find('p', id='multiline')
    assert res.get_text(' ', strip=True) == 'Multiline text'

    # search by text
    res = soup.find('a', text='No href')
    assert res.string == 'No href'


def test_empty_attr(soup):
    res = soup.find_all('a', href='')

    assert len(res) == 2


def test_sibling(soup):
    res = soup.find('div', id='first').find_next_sibling('p')
    assert res['id'] == 'sibling'


def test_following(soup):
    base_res = soup.find('div', id='first')

    res = base_res.find_next('p')
    assert res['id'] == 'following'

    # in this case find should works like find_next
    res = base_res.find('p')
    assert res['id'] == 'following'


def test_attr_contains(soup):
    res = soup.find_all('h1', class_='multiple-value')
    assert len(res), 1


def test_recursive(soup):
    base_res = soup.find('table', class_='recursive')
    res = []
    for row in base_res.find_all('tr', recursive=False):
        res.extend(row.find_all('td', recursive=False))

    assert len(res) == 2

    assert res[0].get_text(strip=True) == 'Inner row'
    assert res[1].get_text(strip=True) == 'Row'


def test_select(soup):
    res = soup.select('span.strikeout.body')
    assert len(res) == 1


def test_new_tag(soup_cls):
    soup = soup_cls('<b></b>')
    original_tag = soup.find('b')

    new_tag = soup.new_tag('a', attrs={'href': 'http://www.example.com'})
    original_tag.append(new_tag)
    assert str(original_tag) == '<b><a href="http://www.example.com"></a></b>'

    new_tag.string = 'Link text.'
    assert str(original_tag) == '<b><a href="http://www.example.com">Link text.</a></b>'


def test_extract(soup_cls):
    soup = soup_cls('<a>1</a><test>2</test><a>3</a><b>4</b>')
    test_tag = soup.find('test').extract()
    assert str(test_tag) == '<test>2</test>'
    assert str(soup) == '<html><body><a>1</a><a>3</a><b>4</b></body></html>'


def test_replace_with(soup_cls):
    soup = soup_cls('<a><inner>2</inner></a><a>3</a><b>4</b>')
    original_tag = soup.find('a')
    original_tag.find('inner').replace_with(soup.new_tag('new_inner'))
    assert str(original_tag) == '<a><new_inner></new_inner></a>'
