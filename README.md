stedwards_books
===============

A script to scrape the St. Edwards web page to find as much textbook information with minimal effort.

Requirements
============
- Python 3.3

Notes
=====
- This isn't the prettiest thing, it was just a fun thing to do on a boring Sunday night while I was waiting for Breaking Bad.
- If you want to run it yourself, know that there is not multiprocessing or threading, so it's slow as all hell.
- It's not perfect, a few things I know are wrong:
    - It only charts sections 1-10, loading the next set is done with js on the library page and I didn't want to mess with that.
    - If a course has no materials, it will not show up in the output.
- Want to make this better? Please do, fork and pull as much as you'd like.
