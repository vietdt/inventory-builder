import os
import urlparse
import logging

from crawler import StandardCrawler

class CaabCrawler(StandardCrawler):
    """
    caab custom crawler
    """
    logger = logging.getLogger('CAAB Crawler')
    hdlr = logging.FileHandler('caab_crawler.log') # FileHandler logs to file
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    ch = logging.StreamHandler() # StreamHandler logs to console
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    logger.info('Start crawling ...')

    def process_row(self, url, title='', response=None):
        """
        Override default behaviour of process_row
        """
        parsed_url = urlparse.urlparse(url)
        path = parsed_url.path
        # get url extension
        ext = os.path.splitext(path)[1]
        # calculate type
        if ext in self.html_exts:
            itemtype = 'HTML'
        elif ext == '.pdf':
            itemtype = 'PDF'
        else:
            itemtype = 'Unknown'
        # use filename when no title found
        if not title:
            title = urlparse.unquote(path.split('/')[-1])
        # remove filename in path
        path = '/'.join(path.split('/')[:-1])+'/'
        return itemtype, title, path, url

# initiate a crawler instance
caab_crawler = CaabCrawler('http://caab.org/', output_filename='caab_inv')
# start crawling
caab_crawler.crawl()
