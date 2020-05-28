import requests
import json
import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo

from exceptions import MetadataException

class Metadata:
    """Store and process page metadata"""
    def __init__(self, cfg):
        self.top_image = ''
        self.keywords = ''
        self.title = ''
        self.description = ''
        self.url = ''
        self._cfg = cfg

    def _extract_meta_safe(self, soup, attributes):
        for a in attributes:
            node = soup.find('meta', a)
            if node:
                content = node.get('content')
                if content:
                    return content
        return ''

    def get_metadata(self, url):
        """Given a url, download the page and extracts metadata"""
        self.url = url
        parsed_uri = urlparse(url)
        self.title = '{uri.netloc}'.format(uri=parsed_uri)

        headers = {
            'User-Agent': self._cfg.get('USER_AGENT'),
            'referer': self._cfg.get('REFERER') 
        }

        page = requests.get(url, headers=headers)

        if page.status_code!=200:
            raise MetadataException('Url returned status != 200')
        try:
            soup = BeautifulSoup(page.content, 'lxml')
        except Exception as e:
            raise MetadataException('Html cannot be parsed')

        if not soup:
            raise MetadataException('DOM is empty')

        soup_head = soup.find('head')
        if not soup_head:
            raise MetadataException('No head in html')

        new_url = self._extract_meta_safe(soup_head, [{'property':'og:url'},
                                                {'name':'twitter:url'}])
        if new_url:
            self.url = new_url

        # extracting title
        new_title = self._extract_meta_safe(soup_head,
                                           [{'property':'og:title'},
                                            {'name':'title'},
                                            {'name':'twitter:title'}])
        if not new_title:
            title_tag = soup_head.find('title')
            if title_tag:
                new_title = title_tag.text

        if new_title and len(new_title):
            self.title = new_title

        #extracting description
        self.description = self._extract_meta_safe(soup_head,
                                                 [{'property':'og:description'},
                                                  {'name':'description'},
                                                  {'name':'twitter:description'}])

        # extracting image
        self.top_image = self._extract_meta_safe(soup_head,
                                               [{'property':'og:image'},
                                                {'name':'twitter:image'},
                                                {'name':'thumb'}])
        # extract keywords
        self.keywords = self._extract_meta_safe(soup_head, [{'name':'keywords'}])
        if self.keywords:
            self.keywords = [k.strip() for k in self.keywords.split(',')]

    def to_json(self):
        """ return a json for the metadata stored"""
        return json.dumps({
            'top_image': self.top_image,
            'keywords': self.keywords,
            'title': self.title,
            'description': self.description,
            'url': self.url
        })


def extract_url(text):
    """Extract the url from a string"""
    reg = re.search("(?P<url>https?://[^\s]+)", text)
    if reg:
        return reg.group("url")


def post_wordpress(cfg, date, author, metadata):
    """ Send the data to wordpress and publish the article"""
    wp_url = 'https://' + cfg.get('WP_DOMAIN') + '/xmlrpc.php'
    wp = Client(wp_url, cfg.get('WP_USER'), cfg.get('WP_PWD'))
    post = WordPressPost()
    post.title = metadata.title
    post.content = '<img class="aligncenter" width="300px" src="%s"> <br/>%s<br/>%s' \
        %(metadata.top_image,
          metadata.description,
          metadata.url)
    if metadata.keywords:
        post.terms_names = {'post_tag': metadata.keywords, 'category': metadata.keywords}
    post.post_status = 'publish'
    wp.call(NewPost(post))
