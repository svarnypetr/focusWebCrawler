#!/usr/bin/env python2.7

import re

from webcrawler import WebCrawler

cnn_url_regex = re.compile('(?<=[.]cnn)[.]com')


# (?<=[.]cnn)[.]com regular expression does the following:
# 1) match '.com' exactly
# 2) then looking backwards from where '.com' was found it attempts to find '.cnn'

w = WebCrawler(cnn_url_regex)
w.start_crawling(['http://edition.cnn.com/'], 4)


# TODO: Make craaler geweral, get negexp from the input line of the file.
