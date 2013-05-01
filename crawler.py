import os
from datetime import datetime
import urllib2
from urlparse import urlparse
import csv
import logging

import mechanize

class StandardCrawler(object):
    """
    A basic web crawler that helps build a website inventory easily.
    """

    def __init__(self, base_url, html_exts=[], media_exts=[],
                 output_filename='', timeout=60.0,
                 log_filename='crawler', log_level=logging.INFO,
                 verbose=False):
        self.base_url = base_url
        # get the hostname from base_url
        self.base_hostname = urlparse(base_url).hostname
        # initiate the visited url set
        self.visited_urls = set()
        # initiate a browser instance
        self.browser = mechanize.Browser()
        # if this option is set, only urls endswith these exts are browsable by the crawler
        self.html_exts = html_exts
        # urls endswith media_exts will not be opened but will be written in output file
        self.media_exts = media_exts
        # to store extracted data
        self.rows = []
        # name of output file
        self.output_filename = output_filename
        # timeout for request
        self.timeout = timeout
        # configure logger
        self.config_logger(log_filename, log_level)
        # determine whether to log successful results
        self.verbose = verbose

    def config_logger(self, name, level):
        """
        Configure logger with file and stream handlers
        """
        self.logger = logging.getLogger(name)
        hdlr = logging.FileHandler('%s.log' % name) # FileHandler logs to file
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        ch = logging.StreamHandler() # StreamHandler logs to console
        self.logger.addHandler(ch)
        self.logger.setLevel(level)
        self.logger.info('Start crawling ...')

    def crawl(self, start_url):
        """
        Crawl all links recursively.
        """
        if len(self.visited_urls) > 50: return
        # advoid duplicates
        if start_url in self.visited_urls: return
        # remember the url
        self.visited_urls.add(start_url)
        # open a new page
        try:
            # open a URL without visiting it, we check the subtype first
            resp = self.browser.open_novisit(start_url, timeout=self.timeout)
            subtype = resp.info().subtype
            # visit the opened response if subtype is html
            if subtype == 'html':
                self.browser.visit_response(resp, self.browser.request)
                # set new response
                resp = self.browser.response()
            # don't record the homepage
            if start_url != self.base_url:
                # process the output
                self.insert_row(start_url, resp)
            # skip next if it's not a html response
            if subtype != 'html':
                return
        except urllib2.HTTPError, e:
            self.logger.error('%d HTTPError: %s' % (e.getcode(), start_url))
            return

        next_urls = set()
        # process all links in page
        for link in self.browser.links():
            # parse the link url
            link_url = link.url
            url = urlparse(link_url)
            # skip if not http link
            if url.scheme and url.scheme not in ['http', 'https']: continue
            # skip if external link
            if url.hostname and self.base_hostname not in url.hostname: continue
            # get url extension
            ext = os.path.splitext(url.path)[1]
            if not url.hostname:
                # convert to absolute URL
                link_url = self.clean_url(link_url)
            # don't browse for urls that endswith media_exts
            if ext in self.media_exts:
                # write output for this media url
                self.insert_row(link_url)
                # remember the url as visited
                if link_url not in self.visited_urls:
                    self.visited_urls.add(link_url)
                continue
            # if html_exts is set, then skip all urls that not endswith html_exts
            if self.html_exts and ext not in self.html_exts:
                continue
            # save url for recursion
            if link_url not in self.visited_urls:
                next_urls.add(link_url)
        # start recursion
        for url in next_urls:
            self.crawl(url)

    def clean_url(self, url, response=None):
        """
        string URL -- convert to absolute URL
        """
        if response:
            base_url = response.geturl()
        else:
            base_url = self.base_url
        # use mechanize.urljoin
        return mechanize.urljoin(base_url, url)

    def insert_row(self, url, response=None):
        """
        Store crawled data into a sequence
        """
        row = self.process_row(url, response)
        self.rows.append(row)
        if self.verbose:
            self.logger.info('200 OK: %s' % url)

    def process_row(self, url, response=None):
        """
        Process data to generate a csv row.
        Can be modified by extender class to generate different information.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        title = path.split('/')[-1]
        return title, path, url

    def write_output(self):
        """
        Write the output as a csv file in data/ folder
        """
        csvfilename = 'data/%s-%s.csv' % (self.output_filename, datetime.now().strftime('%Y%m%d-%H%M%S'))
        with open(csvfilename, 'wb') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerows(self.rows)

    def run(self):
        """
        Run the crawler
        """
        self.crawl(self.base_url)
        if self.output_filename:
            self.write_output()
        self.logger.info('... End crawling')

