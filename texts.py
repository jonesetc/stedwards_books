from html.parser import HTMLParser
from urllib.request import build_opener, HTTPCookieProcessor
from http.cookiejar import CookieJar
from csv import writer, QUOTE_ALL
import re


jar = CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))

section_re = re.compile(r'Section: (?P<section>\d\d)')

BASE_URL = 'https://admin.stedwards.edu'
COURSE_PAIRS = []

class ScheduleParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(ScheduleParser, self).__init__(*args, **kwargs)
        self.course = False
        tmp_info = None

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        if ('style', 'font-weight:bold;') in attrs:
            self.course = True
            attrs = dict(attrs)
            self.tmp_info = attrs['href']

    def handle_endtag(self, tag):
        if tag == 'a':
            self.course = False

    def handle_data(self, data):
        if self.course:
            COURSE_PAIRS.append((data, self.tmp_info))

class CourseParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(CourseParser, self).__init__(*args, **kwargs)
        self.lib_url = ''

    def handle_starttag(self, tag, attrs):
        if ('target', '_blank') in attrs:
            attrs = dict(attrs)
            self.lib_url = attrs['href']

class LibraryParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super(LibraryParser, self).__init__(*args, **kwargs)
        self.section = ''
        self.required = ''
        self.title = ''
        self.author = ''
        self.edition = ''
        self.isbn = ''
        self.in_section_span = False
        self.in_required_span = False
        self.in_title_span = False
        self.in_author_span = False
        self.in_edition_span = False
        self.in_isbn_span = False
        self.section_info = []

    def handle_starttag(self, tag, attrs):
        if tag != 'span':
            return
        attrs = dict(attrs)
        if 'id' not in attrs:
            return
        if attrs['id'].endswith('lblCourseInfo'):
            self.in_section_span = True
        elif attrs['id'].endswith('lblItemRequirement'):
            self.in_required_span = True
        elif attrs['id'].endswith('lblItemTxtTitle'):
            self.in_title_span = True
        elif attrs['id'].endswith('lblItemTxtAuthor'):
            self.in_author_span = True
        elif attrs['id'].endswith('lblItemTxtEdition'):
            self.in_edition_span = True
        elif attrs['id'].endswith('lblItemTxtISBN'):
            self.in_isbn_span = True

    def handle_endtag(self, tag):
        if tag == 'span':
            self.in_section_span, self.in_required_span,  self.in_title_span, self.in_author_span, self.in_edition_span, self.in_isbn_span = False, False, False, False, False, False

    def handle_data(self, data):
        if self.in_section_span:
            results = section_re.search(data)
            self.section = results.group('section').strip() if results else '01'
        elif self.in_required_span:
            self.required = data.strip()
        elif self.in_title_span:
            self.title = data.strip()
        elif self.in_author_span:
            self.author = data.strip()
        elif self.in_edition_span:
            self.edition = data.strip()
        elif self.in_isbn_span:
            self.isbn = data.strip()
            self.section_info.append((self.section, self.required, self.title, self.author, self.edition, self.isbn))

with open('books.csv', 'w') as db:
    csvwriter = writer(db, quoting=QUOTE_ALL)
    csvwriter.writerow(('course', 'section', 'required', 'title','author','edition','isbn'))
    with opener.open(BASE_URL+'/schedule/13FAUG.htm') as schedule:
        parser = ScheduleParser()
        parser.feed(schedule.read().decode(encoding='ISO-8859-1'))

        for course_pair in COURSE_PAIRS:
            parser = CourseParser()
            with opener.open(BASE_URL+course_pair[1]) as course:
                parser.feed(course.read().decode(encoding='ISO-8859-1', errors='ignore'))
                lib_url = parser.lib_url
                parser = LibraryParser()
                with opener.open(lib_url) as library:
                    parser.feed(library.read().decode(encoding='ISO-8859-1', errors='ignore'))
                    for row in parser.section_info:
                        csvwriter.writerow((course_pair[0], row[0], row[1], row[2], row[3], row[4], row[5]))
