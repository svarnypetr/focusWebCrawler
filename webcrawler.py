import urllib
import socket
import httplib
import re

from parser import MyHTMLParser

socket.setdefaulttimeout(10)


class WebCrawler(object):
    """A simple web crawler"""

    link_dict = {}
    initial_depth = 0
    #filter_list = []
    parser = 0
    re_compiled_obj = 0

    class PageInfo:
        """ i store info about a webpage here """
        has_been_scraped = 0
        word_dict = {}

    def __init__(self):
        #self.filter_list.append(self.Filter(1,'.cnn.'))
        self.parser = MyHTMLParser()

    def get_page(self, url):
        """ loads a webpage into a string """
        page = ''
        try:
            f = urllib.urlopen(url=url)
            page = f.read()
            f.close()
        except IOError:
            print "Error opening {}".format(url)
        except httplib.InvalidURL, e:
            print "{} caused an Invalid URL error.".format(url)
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
        return page

    def check_filters(self, url):
        """ If the url_str matches any of the
        enabled filter strings
        then put the url in the dictionary """
        match = self.re_compiled_obj.search(url)
        #print "match = {}".format(match)
        return match

    def find_h1_tag(self, s, pos):
        """ finds the first <h1> tag """
        start = s.find('<h1>', pos)
        end = s.find('</h1>', start)
        return start, end

    def save_tag_text(self, tag, d):
        """ stores each word in the tag in a dictionary """
        if tag != 0:
            token_list = tag.text.split(' ')
            for token in token_list:
                #print 'token = {}'.format(token)
                if token in d:
                    d[token] = d[token] + 1
                else:
                    d[token] = 1
        return d

    def save_page_text(self, page_str):
        """ Save all important text on the page """
        offset = 0
        d = {}

        while offset != -1:
            start, end = self.find_h1_tag(page_str, offset)
            offset = end

            if start != -1 and end != -1:
                h1_tag = page_str[start:end+5]
                #print h1_tag
                self.parser.clear_tag_list()
                # turn text into linked list of tags
                # only feed part of the page into the parser
                self.parser.feed(h1_tag)
                #self.parser.pretty_print_tags()
                tag = self.parser.find_first_tag('h1')
                # add words from tag into the dictionary
                d = self.save_tag_text(tag, d)
        return d

    def save_all_links_on_page(self, page_str, limit):
        """ Stores all links found on the current page in a dictionary """
        d = {}
        offset = 0
        i = 0
        num_pages_filtered = 0
        num_duplicate_pages = 0
        while offset != -1:
            if i == limit:
                break
            offset = page_str.find('<a href="http', offset)
            if offset != -1:
                start = page_str.find('"', offset)
                end = page_str.find('"', start+1)
                link = page_str[start+1:end]
                # don't just save all the links
                # filter the links that match specified criteria
                if self.check_filters(link):
                    if link not in self.link_dict:
                        # adding link to global dictionary
                        self.link_dict[link] = self.PageInfo()
                        # adding link to local dictionary
                        d[link] = self.PageInfo()
                    else:
                        num_duplicate_pages = num_duplicate_pages + 1
                else:
                    num_pages_filtered = num_pages_filtered + 1
                offset = offset + 1
            i = i + 1
        print "{} out of {} links were filtered".format(num_pages_filtered, i)
        print "{} out of {} links were duplicates".format(num_duplicate_pages, i)
        #print "{} links are being returned from save_all_links".format(len(d))
        return d

    def save_all_links_recursive(self, links, depth, limit):
        """ Recursive function that
            1) converts each page (link) into a string
            2) stores all links found in a dictionary """
        d = {}

        print "We are {} levels deep".format(self.initial_depth - depth)

        if depth != 0:
            depth = depth - 1
            urls = links.viewkeys()
            #print "There are {} urls".format(len(urls))
            for url in urls:
                print "trying to get {} over the internet".format(url)
                page_str = self.get_page(url)
                print "done getting {} over the internet".format(url)
                self.link_dict[url].word_dict = self.save_page_text(page_str)
                d = self.save_all_links_on_page(page_str, limit)
                self.link_dict[url].has_been_scraped = 1
                # d contains all the links found on the current page
                self.save_all_links_recursive(d, depth, limit)

    def get_regex_filter(self, seed_urls):
        """Make regex filter based on the seed urls."""
        #TODO: raise error if url malformed {not capable of getting RE}
        #cnn_url_regex = re.compile('(?<=[.]cnn)[.]com')
        reg_list = []
        for url in seed_urls:
            reg_list.append(self.get_domain(url))
        reg_string = '|'.join(reg_list)
        regex_filter = re.compile('(' + reg_string + ')')
        return regex_filter

    def get_domain(self, url):
        if "/" in url:
            dom = url[url.find("//") + 2:]
            dom = dom[:dom.find("/")]
        else:
            dom = url
        print(dom)
        if "." in dom:
            dom = dom.replace(".", ")[.]")
            dom = dom.replace(")[.]", "(?<=[.]", 1)
            dom = dom[dom.find("("):]
        else:
            raise ValueError('Expected a usual URL.')
        return dom

    def start_crawling(self, seed_urls, depth, limit=60):
        """ User calls this function to start crawling the web """
        d = {}
        self.link_dict.clear()
        #self.re_compiled_obj = re.compile('(?<=[.]aktualne)[.]cz')
        self.re_compiled_obj = self.get_regex_filter(seed_urls)

        # init global dictionary variable to the seed url's passed in
        for page in seed_urls:
            self.link_dict[page] = self.PageInfo()
            d[page] = self.PageInfo()
        self.initial_depth = depth
        # start a recursive crawl
        # can't pass in self.link_dict because then i get a RuntimeError: dictionary changed size during iteration
        self.save_all_links_recursive(d, depth, limit)

    def print_all_page_text(self):
        """ prints contents of all the word dictionaries """
        for i in range(len(self.link_dict)):
            page_info = self.link_dict.values()[i]
            url = self.link_dict.keys()[i]
            print 'url = {}, has_been_scraped = {}'.format(url, page_info.has_been_scraped)
            d = page_info.word_dict
            for j in range(len(d)):
                word = d.keys()[j]
                count = d.values()[j]
                print '{} was found {} times'.format(word, count)
