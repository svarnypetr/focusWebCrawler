#!/usr/bin/env python2.7

from webcrawler import WebCrawler

w = WebCrawler()

seed_urls = ['https://www.aktualne.cz/', 'https://www.seznam.cz']

w.start_crawling(seed_urls, 1, 60)
print(len(w.link_dict))
