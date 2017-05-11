#!/usr/bin/env python2.7

from webcrawler import WebCrawler

w = WebCrawler()
w.start_crawling(['http://www.aktualne.cz/'], 1, 180)
