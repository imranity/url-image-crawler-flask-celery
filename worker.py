import os
import re
import time
from celery import Celery
from bs4 import BeautifulSoup
from urllib2 import urlparse, urlopen

env=os.environ
CELERY_BROKER_URL=env.get('CELERY_BROKER_URL','redis://localhost:6379'),
CELERY_RESULT_BACKEND=env.get('CELERY_RESULT_BACKEND','redis://localhost:6379')


celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


@celery.task(name='mytasks.crawl')
def crawls(url):
    urlStream = urlopen(url)
    htmldoc = urlStream.read()
    soup=BeautifulSoup(htmldoc)
    links=[]
    images = soup.findAll("img", {"src":re.compile(r'\.(jpe?g)|(png)|(gif)$')})
    for img in img_links:
        links.append(urlparse.urljoin(url,img["src"]))
    return links