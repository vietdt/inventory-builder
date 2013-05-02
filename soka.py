import os
import cgi
import urlparse
import logging

from mechanize import _sgmllib_copy as sgmllib

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
        # skip sendto_form link
        if url.path.endswith('/sendto_form'): return
        # skip bookmark link
        if url.geturl().startswith('#'): return
        # run default validation
        return self._validate_url(url)

    def process_row(self, url, response=None):
        """
        Override default behaviour of process_row
        """
        parsed_url = urlparse.urlparse(url)
        path = parsed_url.path
        title = None
        # get subtype from response
        resp_info = subtype = None
        if response:
            resp_info = response.info()
            subtype = resp_info.subtype
        # get url extension
        ext = os.path.splitext(path)[1]
        # calculate type
        if subtype:
            # set itemtype by subtype
            itemtype = str.upper(subtype)
            # calculate title
            if subtype == 'html':
                # get browser title
                try:
                    title = self.browser.title()
                except sgmllib.SGMLParseError, e:
                    # unknown error may occur, skip it
                    self.logger.warning('title parsing error: %s' % url)
            else:
                # get filename from header
                _, params = cgi.parse_header(resp_info.getheader('Content-Disposition', ''))
                title = params.get('filename')
        # get itemtype from ext
        elif ext:
            itemtype = ext[1:].upper()
        else:
            itemtype = 'Unknown'
        # use last component in path as title when nothing found
        if not title:
            title = urlparse.unquote(path.split('/')[-1])
        # remove last component in path
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
