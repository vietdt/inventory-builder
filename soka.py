import os
import urlparse
import logging

from crawler import StandardCrawler

class SokaCrawler(StandardCrawler):
    """
    sokaspirit custom crawler
    """

    def validate_url(self, url):
        """
        Override default behaviour of validate_url
        """
        # skip language changing link
        if 'set_language=' in url.query: return
        # run default validation
        return self._validate_url(url)

    def process_row(self, url, response=None):
        """
        Override default behaviour of process_row
        """
        parsed_url = urlparse.urlparse(url)
        path = parsed_url.path
        # get subtype from response
        subtype = None
        if response:
            subtype = response.info().subtype
        # get url extension
        ext = os.path.splitext(path)[1]
        # calculate type
        if subtype:
            # set itemtype by subtype
            itemtype = str.upper(subtype)
        # get itemtype from ext
        elif ext:
            itemtype = ext[1:].upper()
        else:
            itemtype = 'Unknown'
        # calculate title
        if subtype == 'html':
            # get browser title
            title = self.browser.title()
        else:
            # use filename when no title found
            title = urlparse.unquote(path.split('/')[-1])
        # remove filename in path
        path = '/'.join(path.split('/')[:-1])+'/'
        return itemtype, title, path, url

# initiate a crawler instance
soka_crawler = SokaCrawler('http://www.sokaspirit.org/',
                           output_filename='soka_inv',
                           log_filename='soka_crawler',
                           timeout=90.0,
                           verbose=True)
# start crawling
soka_crawler.run()
