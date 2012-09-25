from twython import Twython
from nava_rank import db
from nava_rank import Tweet
import math, sched, time, collections, re
from threading import Timer
from datetime import datetime, timedelta 
from nava_rank import tavorite, tweet_age_in_hours, tweets_age_for_view, following




def get_tweets_update_db():
    get_tweets =  tavorite.getHomeTimeline(count=200, include_entities=1, include_retweets=1)
    for x in get_tweets:
        tweet = Tweet(x)
        tweet_in_db = Tweet.query.filter_by(tweet_id=tweet.tweet_id).first()
        if tweet_in_db:
            if tweet_age_in_hours(tweet_in_db) < 14:
                if tweet_in_db.retweet_count < tweet.retweet_count:
                    tweet_in_db.retweet_count = tweet.retweet_count
                    db.session.commit()
        else:
            if tweet.url_exists:
                try:
                    db.session.add(tweet)
                    db.session.commit()
                except:
                    db.session.rollback()
    print "update successful"



# STILL NOT GOOD ENOUGH. FASTE FASTER FASTER

def update_averages_and_std_deviation(tweets_in_db):
    
    """Includes retweets of all tweets. Should it be only links?"""
    """tweets_in_db == Tweet.query.all()"""

    link_counter = links_number_of_times(tweets_in_db)

    for z in following:
        user = Tweet.query.filter_by(user_id=z).all()
        retweet_counts = [y.retweet_count for y in user]
            # average retweet count of user_id

        if len(retweet_counts) != 0:
            average = sum(retweet_counts)/len(retweet_counts)
            calculate = sum([pow((g-average), 2) for g in retweet_counts])
            standard_deviation = math.sqrt(calculate/len(retweet_counts))
        else:
            average = 0
            calculate = 0
            standard_deviation = 0
        
        Tweet.query.filter_by(user_id=z).update(dict(average_rt_count=average, std_deviation=standard_deviation))
        try: 
            db.session.commit()
        except:
            db.session.rollback()

        for x in user:
            #if tweet_age_in_hours(x) < 1680:
            if standard_deviation != 0:
                x.std_dev_sigma    = (x.retweet_count - average)/standard_deviation
            if len(retweet_counts) < 30 and x.std_dev_sigma > 3:
                x.std_dev_sigma = 3.0

            if len(retweet_counts) < 5:
                x.std_dev_sigma = 0
            
            tweet_hour_age = tweet_age_in_hours(x)

            number_of_times_retweeted = times_appears_in_stream(x.link, link_counter)

            points = (10*(x.std_dev_sigma))*number_of_times_retweeted
            score_with_time = hacker_news(points, tweet_hour_age)

            x.score = round(points)
            x.score_with_time = score_with_time
            try:
                db.session.commit()
            except:
                db.session.rollback()





#Automate get new tweets every X minues and update the DB    
def update_every_minute():
    s = sched.scheduler(time.time, time.sleep)
    print "updating feed beginning"
    s.enter(260, 1, get_tweets_update_db, ())
    s.run()
    update_every_minute()
    """To continously loop recursive call update_every_minute()"""



def media_in_link(item):
    """filter() assumes None to be True"""
    things_to_remove = ['http://instagr', 'twitpic', 'yfrog', 'youtube', 'vimeo', '.jpg', '.jpeg', '.png', '.gif']
    filtr = []
    for x in things_to_remove:
        if x in item.tweet.link:
            filtr.append(False)
        else: 
            filtr.append(True)
    f = False not in filtr
    return f


def filter_for_double_links(all_links):
    filtered_links = []

    tweet_links = []

    for lnk in all_links:
        link = lnk.link
        user_id = lnk.user_id

        if (link, user_id) not in filtered_links:

            x = (link, user_id)

            filtered_links.append(x)

            tweet_links.append(link)

    return tweet_links

def links_number_of_times(Tweets):
    """tweets = Tweet.query.all()"""
    tweets = [x for x in Tweets if x.url_exists] 
    links = filter_for_double_links(tweets)
    cnt = collections.Counter(links).most_common(100)
    return cnt

def times_appears_in_stream(link, counter):
    links_only = []
    for x in counter:
        links_only.append(x[0])
    if link not in links_only:
        return 1
    else:
        for x in counter:
            if link in x[0]:
                if x[1] == 1:
                    return 1
                if x[1] == 2:
                    return pow(1.25, 2)
                if x[1] > 2:
                    return pow(1.25, 3)
                    


def hacker_news(votes, item_hour_age, gravity=1.8):
    return votes/pow((item_hour_age+2), gravity)


#def list_of_links(sorted_by=Nava_rank.score):
#    def filter_for_double_links(nava_rank_objects):
#        filtered_links = []
#        tweets = []
#        for lnk in nava_rank_objects:
#            url = lnk.tweet.link
#            user_id = lnk.tweet.user_id
#            if (url, user_id) not in filtered_links:
#                unique_link_from_user = (url, user_id)
#                filtered_links.append(unique_link_from_user)
#                tweets.append(lnk)
#        return tweets
#    start = Nava_rank.query.order_by(sorted_by).all()
#    all_links = [x for x in start if x.tweet.url_exists]
#    all_links.reverse()
#    links = filter(media_in_link, all_links)
#    links = filter_for_double_links(links)
#    links = links[0:30]
#    return links
