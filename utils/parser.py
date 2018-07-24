import logging
import traceback

import numpy as np
import multiprocessing
import urllib.request
import urllib.error
from abc import abstractmethod
from bs4 import BeautifulSoup

from utils.config import config
from utils.config import shares as shares_list
from common.db_manager import DbManager

log = logging.getLogger(__name__)
logging_format = '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -50s %(lineno) -5d: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)


class BaseParser:
    def __init__(self):
        self._config = config.copy()
        self._shares_list = shares_list
        self.db_manager = DbManager()

    @abstractmethod
    def parse(self, q, r):
        """ABC.parse"""
        pass

    @abstractmethod
    def _build_data(self, soup, share):
        """ABC._build_data"""
        pass

    def call_parse(self, num_procs):
        sources = [x.lower().strip() for x in self._shares_list]
        parsed = []

        q = multiprocessing.JoinableQueue()
        r = multiprocessing.JoinableQueue()
        procs = []
        for i in range(num_procs):
            p = multiprocessing.Process(target=self.parse, args=(q, r,))
            p.daemon = True
            p.start()
            procs.append(p)

        for item in sources:
            q.put(item)
        for i in range(num_procs):  # Terminate
            q.put(None)
        while True:
            if r.qsize() == len(sources):  # Wait for result queue has all data
                break
        while not r.empty():
            x = r.get()
            parsed.append(x)
        return parsed

    def _retrieve(self, share, suffix, page_suffix=None, page_number=None):
        """Retrieves data by url"""
        url = self._config['BASE_URL'] + share + suffix
        if page_suffix and page_number:
            url = url + str(page_suffix) + str(page_number)

        log.warning('Getting share (%s) data from url: %s' % (str(share), str(url)))
        try:
            content = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise 'Content by this url can not be found. Url: %s' % str(url)
            else:
                raise 'Unknown HTTP exception. Check Internet connection? Exception: %s' % (traceback.format_exc())

        content = content.read()
        soup = BeautifulSoup(content, 'html.parser')
        return soup

    def _get_general_table(self, soup):
        """Finds general table with data"""
        table = self._get_tag_by_div_class(soup, 'genTable')
        try:
            assert(table is not None)
        except AssertionError:
            log.error('Table is disappeared!')
            raise AssertionError
        return table

    @staticmethod
    def _get_headers(table):
        """Finds headers inside the table"""
        headers = []
        for tag in table.find_all('th'):
            if not tag.a:
                headers.append(tag.text)
            else:
                headers.append(tag.text.strip().split('\r\n')[0])

        # TODO also instead of cycle we can do like this:
        # TODO headers.append([x.text.strip().split('\r\n')[0] for x in table.find_all('th') if not tag.a else x.text])
        # But it's not clear for reader and for guy who will support this code.
        try:
            assert(headers is not None)
        except AssertionError:
            log.error('Headers are empty! Check the markup.')
            raise AssertionError

        return headers

    @staticmethod
    def _get_values(headers_len, share_id, command):
        """Finds values inside the table"""
        values = []
        if command[0].contents[0] == '\n':   # If resource doesn't show first line in browser, but returns it
            command = command[headers_len:]
        for count, tag in enumerate(command, 1):
            values.append(tag.text.strip().replace(',', ''))
            if not count % headers_len:             # Every len(headers) iteration we insert the share_id
                values.append(share_id)

        try:
            assert(values is not None)
        except AssertionError:
            log.error('Values are empty! Check the markup.')
            raise AssertionError
        try:
            values = np.reshape(values, (-1, headers_len + 1))
        except Exception as e:
            log.error('Something goes wrong with NumPy. Check it.')
            raise traceback.format_exc(e)

        return values

    @staticmethod
    def _get_tag_by_div_class(soup, class_):
        """You understand whats this method do according to it's name?"""
        return soup.find('div', {'class': str(class_)})

    @staticmethod
    def _get_tag_by_div_id(soup, id_):
        """You understand whats this method do according to it's name?"""
        return soup.find('div', {'id': str(id_)})


class ShareParser(BaseParser):
    def __init__(self):
        super().__init__()

    def parse(self, q, r):
        """Parses shares"""
        suffix = self._config['SHARES_SUFFIX']
        parsed = []
        while True:
            share = q.get()
            if share is None:  # detect termination
                break
            log.warning('Parsing share %s. ' % (str(share)))
            parsed.append(self._build_data(self._retrieve(share, suffix), share))
            q.task_done()
        if parsed:
            r.put(parsed)

    def _build_data(self, soup, share_id):
        """Builds data from html"""
        table = self._get_general_table(soup)
        headers = self._get_headers(table)
        data = self._get_values(len(headers), share_id, command=table.find('tbody').find_all('td'))
        return data


class TradeParser(BaseParser):
    def __init__(self):
        super().__init__()

    def parse(self, q, r):
        """Parses trades"""
        parsed = []
        suffix = self._config['TRADES_SUFFIX']
        page_suffix = self._config['PAGE_SUFFIX']

        while True:
            share = q.get()
            if share is None:  # detect termination
                break
            log.warning('Parsing share %s. ' % (str(share)))
            share_id = self.db_manager.insert_share(share)
            page_count = self._get_page_count(self._retrieve(share, suffix))
            if page_count > self._config['PAGE_COUNT_LIMIT_TO_PARSE']:
                page_count = self._config['PAGE_COUNT_LIMIT_TO_PARSE']  # According to the test's condition
            for page_number in range(1, page_count + 1):
                parsed.append(self._build_data(self._retrieve(share, suffix, page_suffix, page_number), int(share_id)))
            q.task_done()
        if parsed:
            r.put(parsed)

    def _build_data(self, soup, share_id):
        """Builds data from html"""
        table = self._get_general_table(soup)
        headers = self._get_headers(table)
        data = self._get_values(len(headers), share_id, command=table.find_all('td'))
        return data

    def _get_page_count(self, soup):
        """Get last pages count for trades history"""
        page_count_html_part = self._get_tag_by_div_id(soup, 'pagerContainer')
        last_page_tag = page_count_html_part.find('a', {'id': 'quotes_content_left_lb_LastPage'})
        last_page_url = last_page_tag.attrs['href']
        assert(last_page_url is not None)
        return int(last_page_url.split('=')[1].replace('"', ''))
