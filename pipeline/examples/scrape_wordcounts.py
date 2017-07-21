#!/usr/bin/env python
"""**scrape_wordcounts** handles downloading the some of the
top works on Project Gutenberg and parsing their text into word count
dictionaries.  These are then combined into a single corpus count using a Reduce
stage. Multiple workers are utilized for stages, especially those that may be io
bound while downloading as an example of concurrency.

>>> from pipeline import pipeline, Stage, Reduce
>>> start_url = ['https://www.gutenberg.org/browse/scores/top']
>>> p = pipeline([Stage(top_books, returns_many=True),
...               Stage(drop_random, n_workers=5),
...               Stage(to_book_url, n_workers=10),
...               Stage(sleep_random, n_workers=10),
...               Stage(get_text, n_workers=10),
...               Stage(count_words, n_workers=10),
...               Stage(remove_full_text, n_workers=10),
...               Reduce(corpus_count, initial_value={}),
...               ], start_url)
>>> p.join() # doctest: +ELLIPSIS
<pipeline.pipeline.PipelineResult object at 0x...>
>>> p.values
[]
"""
from gevent import monkey
monkey.patch_all() # noqa

from pipeline import DROP
import gevent
import random
from collections import defaultdict

import requests
from lxml import html


def top_books(link):
    page = requests.get(link)
    tree = html.fromstring(page.content)
    urls = tree.xpath('//h2[@id="books-last1"]/../ol/li/a/@href')
    urls = [u for u in urls if 'ebooks' in u]
    return urls


def drop_random(url):
    if random.uniform(1, 20) == 20:
        return url
    else:
        return DROP


def to_book_url(link):
    book_number = link.replace('/ebooks/', '')
    link = 'https://www.gutenberg.org' + link
    page = requests.get(link)
    tree = html.fromstring(page.content)
    try:
        url = tree.xpath('//a[@type="text/plain"]/@href')[0]
    except:
        try:
            url = tree.xpath('//a[@type="text/plain; charset=utf-8"]/@href')[0]
        except:
            print(url)
    if 'http' not in url:
        url = 'http:' + url
    doc = {'url': url,
           'number': book_number}
    return doc


def get_text(doc):
    text = requests.get(doc['url']).content
    doc.update({'text': text.decode('utf8')})
    return doc


def sleep_random(value):
    gevent.sleep(random.uniform(0, 1))
    return value


def count_words(doc):
    counts = defaultdict(int)
    for word in doc['text'].split(' '):
        word = word.replace('\n', '')
        word = word.replace('\r', '')
        counts[word] = counts[word] + 1
    doc.update({'counts': counts})
    return doc


def remove_full_text(doc):
    del doc['text']
    return doc


def corpus_count(corpus, doc):
    corpus.update({doc['number']: doc})
    if 'counts' not in corpus:
        corpus['counts'] = defaultdict(int)
    for word in doc['counts']:
        corpus['counts'][word] += doc['counts'][word]
    return corpus

if __name__ == "__main__":
    import doctest
    doctest.testmod()
