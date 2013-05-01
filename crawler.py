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
    # configure logger
    logger = logging.getLogger('crawler')

    def __init__(self, base_url, html_exts=['.html', '.php'], media_exts=['.pdf'],
                 output_filename='website_inv', timeout=30.0):
        self.base_url = base_url
        # get the hostname from base_url
        self.base_hostname = urlparse(base_url).hostname
        # initiate the visited url set
        self.visited_urls = set()
        # initiate a browser instance
        self.browser = mechanize.Browser()
        # only urls endswith these html_exts are browsable by this crawler
        self.html_exts = html_exts
        # urls endswith media_exts will not be opened but will be written in output file
        self.media_exts = media_exts
        # write the output as a csv file in data/ folder
        csvfilename = 'data/%s-%s.csv' % (output_filename, datetime.now().strftime('%Y%m%d-%H%M%S'))
        csvfile = open(csvfilename, 'wb')
        self.writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        # timeout for request
        self.timeout = timeout

    def crawl(self, start_url=''):
        """
        Crawl all links recursively.
        """
        # set default url
        if not start_url: start_url = self.base_url
        # advoid duplicates
        if start_url in self.visited_urls: return
        # remember the url
        self.visited_urls.add(start_url)
        # open a new page
        try:
            resp = self.browser.open(start_url, timeout=self.timeout)
            if start_url != self.base_url:
                # write to output
                self.writerow(start_url, self.browser.title())
        except urllib2.HTTPError, e:
            self.logger.error('%d HTTPError: %s' % (e.getcode(), start_url))
            return

        next_urls = set()
        # process all links in page
        for link in self.browser.links():
            # parse the link url
            link_url = link.url
            url = urlparse(link_url)
            # skip if external link
            if url.hostname and self.base_hostname not in url.hostname: continue
            # get url extension
            ext = os.path.splitext(url.path)[1]
            if not url.hostname:
                # convert to absolute URL
                link_url = self.clean_url(link_url)
            # validate extension
            if ext in self.html_exts:
                # save url for recursion
                if link_url not in self.visited_urls:
                    next_urls.add(link_url)
            elif ext in self.media_exts:
                # write output for this pdf url
                self.writerow(link_url)
                # remember the url as visited
                if link_url not in self.visited_urls:
                    self.visited_urls.add(link_url)
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

    def writerow(self, url, title='', response=None):
        """
        Write crawled data to a csv file
        """
        row = self.process_row(url, title, response)
        self.writer.writerow(row)

    def process_row(self, url, title='', response=None):
        """
        Process data to generate a csv row.
        Can be modified by extender class to generate different information.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        if not title:
            title = path.split('/')[-1]
        return title, path, url

