import unittest


from bs4 import BeautifulSoup as BS4Soup
from ..fast_soup import FastSoup


class TestFind(unittest.TestCase):
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

    bs4_soup = BS4Soup(data)
    soup = FastSoup(data)

    def test_common(self):
        res1 = self.bs4_soup.find('a')
        res2 = self.soup.find('a')

        self.assertEqual(res1.name, res2.name)

        self.assertEqual(res1.get_text(), res2.get_text())
        self.assertEqual(res1.get_text(strip=True), res2.get_text(strip=True))

        # search by text
        res3 = self.bs4_soup.find('a', text='No href')
        res4 = self.soup.find('a', text='No href')

        self.assertEqual(res3.string, res4.string)

    def test_empty_attr(self):
        res1 = self.bs4_soup.find_all('a', href='')
        res2 = self.soup.find_all('a', href='')

        self.assertTrue(len(res1) == len(res2))

    def test_sibling(self):
        res1 = self.bs4_soup.find('div', id='first').find_next_sibling('p')
        res2 = self.soup.find('div', id='first').find_next_sibling('p')

        self.assertEqual(res1['id'], 'sibling')
        self.assertEqual(res1['id'], res2['id'])

    def test_following(self):
        base_res1 = self.bs4_soup.find('div', id='first')
        base_res2 = self.soup.find('div', id='first')

        res1 = base_res1.find_next('p')
        res2 = base_res2.find_next('p')
        self.assertEqual(res1['id'], 'following')
        self.assertEqual(res1['id'], res2['id'])

        # in this case find should works like find_next
        res1 = base_res1.find('p')
        res2 = base_res2.find('p')
        self.assertEqual(res1['id'], 'following')
        self.assertEqual(res1['id'], res2['id'])

    def test_attr_contains(self):
        res1 = self.bs4_soup.find_all('h1', class_='multiple-value')
        res2 = self.soup.find_all('h1', class_='multiple-value')

        self.assertNotEqual(res1, [])
        self.assertNotEqual(res2, [])

        self.assertTrue(len(res1) == len(res2))


if __name__ == '__main__':
    unittest.main()
