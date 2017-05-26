#!/usr/bin/env python2.7

from webcrawler import WebCrawler

w = WebCrawler()

seed_urls = ['https://www.aktualne.cz/', 'https://www.seznam.cz']

for seed in seed_urls:
    w.start_crawling([seed], 2, 60)
    print(len(w.link_dict))
