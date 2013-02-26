'''
The twitter handler task.
'''

from celery import Celery
celery = Celery('circlejerk-twitter-tasks',
        broker='amqp://guest@localhost')

import twitter

# Be sure to add credentials.py with all the following values:
from credentials import CONSUMER_KEY
from credentials import CONSUMER_SECRET
from credentials import OAUTH_TOKEN
from credentials import OAUTH_SECRET

twitter_client = None

def init_twitter_client(logger):
    global twitter_client
    if twitter_client is None:
        twitter_client = twitter.Twitter(
                auth=twitter.OAuth(
                    OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
        logger.info('Successfully created twitter client.')

import sys
import traceback
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

import remember

@celery.task(
    default_retry_delay=30 * 60, # retry every 30 minutes
    max_retries=5,
    rate_limit=1.0 / (5 * 60) # wait 5 minutes between tweets
)
def post_to_twitter(text, url, force=False):
    logger.info('Setting status to "%s" for url "%s"' % (text, url))
    try:
        init_twitter_client(logger)
        if force or not remember.already_tweeted(url):
            twitter_client.statuses.update(status=text)
            remember.remember_tweet(url)
        else:
            logger.info('Not tweeting "%s": already tweeted url "%s"'
                    % (text, url))
    except:
        logger.error(traceback.format_exc())
