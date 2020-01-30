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
def soup(request, data):
    if request.param == 'bs4':
        return BS4Soup(data, features='lxml')
    else:
        assert request.param == 'fast-soup'
        return FastSoup(data)


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
