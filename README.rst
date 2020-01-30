
FastSoup 

.. image:: https://travis-ci.org/spumer/FastSoup.svg
    :target: https://travis-ci.org/spumer/FastSoup
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/spumer/FastSoup/badge.svg
    :target: https://coveralls.io/github/spumer/FastSoup

=====================================================================================================================================================

BeautifulSoup interface for lxml

Key features
============


* **FAST** search in tree
* **FAST** serialize to str
* BeautifulSoup4 interface to interact with object:

  * Search: ``find``\ , ``find_all``\ , ``find_next``\ , ``find_next_sibling``
  * Text: ``get_text``\ , ``string``
  * Tag: ``name``\ , ``get``\ , ``clear``\ , ``__getitem__``\ , ``__str__``

Install
-------

.. code-block:: bash

   pip install fast-soup==1.0.0

How to use
----------

.. code-block:: python

   from fast_soup import FastSoup

   content = ...  # read some html content
   soup = FastSoup(content)

   # interact like BS4 object
   result = soup.find('a', id='my_link')

   # interact like lxml object
   el = result.unwrap()

FAQ
===

**Q:** BS4 already implement lxml parser. Why i should use FastSoup?

**A:** Yes, BS4 implement **parser**\ , and it's just building the tree. All next interactions proceed with "Python speed":
searching, serialization.
FastSoup internally use lxml and guarantee "C speed".

**Q:** How FastSoup speedup works?

**A:** FastSoup just build **xpath** and execute them. For prevent rebuilding LRU cache used.

**Q:** Why you don't support whole interface? This will be soon?

**A:** I wrote functions which speed up parsing in my projects. Just create a issue or pull request and i think we find the solution ;)

Miscellaneous
-------------

You can got power of BeautifulSoup when wrap your lxml objects, e.g:

.. code-block:: python

   from fast_soup import Tag

   content = ...  # some bytes ready to parse
   context = lxml.etree.iterparse(
       io.BytesIO(content),  ...
   )
   for event, elem in context:
       tag = Tag(elem)

       tag_text = tag.get_text()
       tag_attr = tag['attribute']
