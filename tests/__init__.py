import unittest


from bs4 import BeautifulSoup as BS4Soup
from fast_soup import FastSoup


class BaseTestFind(unittest.TestCase):
    data = '''
    <html>

    <a href="">   It's a text    </a>
    <a>No href</a>

    <div id="first">
        <p id="following"></p>
    </div>

    <p id="sibling">
    </p>

    <h1 class="multiple-value multiple-value2"></h1>
    <h1 class="multiple-value-sub multiple-value2-sub"></h1>

    </html>

    '''

    soup = NotImplemented

    @classmethod
    def setUpClass(cls):
        if cls is BaseTestFind:
            raise unittest.SkipTest("Skip BaseTestFind tests, it's a base class")
        super().setUpClass()

    def test_common(self):
        res = self.soup.find('a')

        self.assertEqual(res.name, 'a')

        self.assertEqual(res.get_text(), '   It\'s a text    ')
        self.assertEqual(res.get_text(strip=True), 'It\'s a text')

        # search by text
        res = self.soup.find('a', text='No href')
        self.assertEqual(res.string, 'No href')

    def test_empty_attr(self):
        res = self.soup.find_all('a', href='')

        self.assertEqual(len(res), 2)

    def test_sibling(self):
        res = self.soup.find('div', id='first').find_next_sibling('p')
        self.assertEqual(res['id'], 'sibling')

    def test_following(self):
        base_res = self.soup.find('div', id='first')

        res = base_res.find_next('p')
        self.assertEqual(res['id'], 'following')

        # in this case find should works like find_next
        res = base_res.find('p')
        self.assertEqual(res['id'], 'following')

    def test_attr_contains(self):
        res = self.soup.find_all('h1', class_='multiple-value')
        self.assertEqual(len(res), 1)



class BS4TestFind(BaseTestFind):
    soup = BS4Soup(BaseTestFind.data)


class FastSoupTestFind(BaseTestFind):
    soup = FastSoup(BaseTestFind.data)


if __name__ == '__main__':
    unittest.main()
