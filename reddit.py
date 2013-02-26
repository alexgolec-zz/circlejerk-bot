'''
The reddit scraping module.
'''
import json
import sys
import traceback
import urllib2

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'circlejerk-pix-bot')]

# Set up logging
import logging
logger = logging.getLogger('reddit_bot')
logger.propagate = True
logger.setLevel(logging.DEBUG)
# TODO: Fix the typo in the logs directory name
fh = logging.FileHandler('/home/pi/logs/circlerk-bot/reddit.py.log')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)

url = 'http://api.reddit.com/r/circlejerk'
logging.info('Fetching, %s' % (url,))
data = json.loads(opener.open(url).read())

def iterate_string_leaves(data, *desired_keys):
    '''
    Iterate over the leaves of the json object. If desired_keys are passed, only
    iterate over the leaves of the object that have the specified keys.
    '''
    # TODO: Convert desired_keys to a set.
    if isinstance(data, dict):
        for key, value in data.iteritems():
            if isinstance(value, basestring):
                if len(desired_keys) == 0:
                    yield key, value
                elif key in desired_keys:
                    yield key, value
            else:
                for item in iterate_string_leaves(value, *desired_keys):
                    yield item
    elif isinstance(data, list):
        for item in data:
            for other_item in iterate_string_leaves(item, *desired_keys):
                yield other_item

import time
from bs4 import BeautifulSoup
import HTMLParser

unescaper = HTMLParser.HTMLParser()

from termcolor import colored
import urlparse
def should_post_image(url,
    image_extensions=set([
        '.gif',
        '.jpg',
        '.jpeg',
        '.png'
    ]),
    hosting_websites = set([
        'imgur.com'
    ])):
    '''
    '''
    if any(url.endswith(extension) for extension in image_extensions):
        return True 
    parsed = urlparse.urlparse(url)
    if any(parsed.netloc.endswith(site) for site in hosting_websites):
        return True
    return False

import remember
import twitter_bot
def do_story(story):
    url = 'http://api.reddit.com'+story['data']['permalink']
    url = url.encode('utf-8', 'replace')
    time.sleep(5)
    logger.info('Fetching %s' % (url,))
    story_data = json.loads(opener.open(url).read())
    for key, value in iterate_string_leaves(story_data, 'body_html'):
        value = unescaper.unescape(value)
        soup = BeautifulSoup(value)
        for anchor in soup.find_all('a'):
            found_url = anchor.attrs['href']
            print colored(found_url, 'green' if
                    should_post_image(found_url)  else 'red')
            if should_post_image(found_url):
                message = str(found_url)
                if not remember.already_tweeted(found_url):
                    logger.info('Emitting url %s' % (found_url,))
                    twitter_bot.post_to_twitter.delay(message, found_url)

for story in data['data']['children']:
    try:
        do_story(story)
    except KeyboardInterrupt:
        break
    except:
        logger.error(traceback.format_exc())
        continue
