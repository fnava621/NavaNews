import sched, time, requests, json, HTMLParser
import urlparse, math, collections, re
from threading import Timer
from flask import *
from flask.ext.sqlalchemy import *
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup
from twython import Twython
#from keys import *  #REMOVE THIS before pushing to git


app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////Users/fernandonava/desktop/Projects/python_projects/tavorite/test-news.db' # REMOVE THIS

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')


db = SQLAlchemy(app)

#tavorite = Twython(app_key=os.environ['CONSUMER_KEY'],
#                   app_secret=os.environ['CONSUMER_SECRET'],
#                   oauth_token=os.environ['ACCESS_TOKEN'],
#                   oauth_token_secret=os.environ['ACCESS_TOKEN_SECRET'])


@app.route('/')
def home():
    links = Tweet.query.filter_by(url_exists=True).order_by(Tweet.score_with_time.desc()).limit(40).all()
    time = tweets_age_for_view(links) 
    #links = list_of_links(Nava_rank.rt_count)

    ### NEEDS A FILTER FOR MEDIA LINKS
    return render_template('show_links.html', links=links, time=time)

@app.route('/best')
def best():
    links = Tweet.query.filter_by(url_exists=True).order_by(Tweet.score.desc()).limit(50).all()
    #links = list_of_links(Nava_rank.rt_count)
    time = tweets_age_for_view(links)

    ###NEEDS A FILTER FOR MEDIA LINKS
    return render_template('best_of_week.html', links=links, time=time)


@app.route('/photos')
def photos():
    photos = Tweet.query.filter(Tweet.picture != unicode("")).order_by(Tweet.date.desc()).limit(50).all()
    return render_template('photos.html', photos=photos)

@app.route('/videos')
def videos():
    youtube = Tweet.query.filter_by(url_exists=True).filter(Tweet.main_url == 'www.youtube.com').order_by(Tweet.score.desc()).limit(50).all()

    vimeo = Tweet.query.filter_by(url_exists=True).filter(Tweet.main_url == 'www.vimeo.com').order_by(Tweet.score.desc()).limit(50).all()

    #start = Nava_rank.query.order_by(Nava_rank.rt_count).all()
    #start.reverse()
    #links = [x for x in start if x.tweet.url_exists]

    videos = youtube + vimeo
    videos = videos[0:30]
    time = tweets_age_for_view(videos)
    return render_template('videos.html', videos=videos, time=time)


class Tweet(db.Model):

    id               = db.Column(db.Integer, primary_key=True)
    tweet            = db.Column(db.UnicodeText)
    screen_name      = db.Column(db.Unicode(256))
    name             = db.Column(db.Unicode(256))
    user_id_str      = db.Column(db.Unicode(256))
    user_id          = db.Column(db.BIGINT)
    user_created_at  = db.Column(db.Unicode(356))
    user_following   = db.Column(db.BIGINT)
    user_followers   = db.Column(db.BIGINT)
    user_url         = db.Column(db.Unicode(400))
    statuses_count   = db.Column(db.BIGINT)
    tweet_created_at = db.Column(db.Unicode(256))
    tweet_id         = db.Column(db.BIGINT)
    text             = db.Column(db.Unicode(400))
    retweeted        = db.Column(db.Boolean)
    url_exists       = db.Column(db.Boolean)
    link             = db.Column(db.Unicode(500))
    main_url         = db.Column(db.Unicode(500))
    profile_picture  = db.Column(db.Unicode(500))
    picture          = db.Column(db.Unicode(500))
    date             = db.Column(db.DateTime)
    page_text        = db.Column(db.UnicodeText)
    retweet_count    = db.Column(db.Integer)
    headline         = db.Column(db.Unicode(500))
    average_rt_count = db.Column(db.Float)
    std_deviation    = db.Column(db.Float)
    std_dev_sigma    = db.Column(db.Float)
    score            = db.Column(db.Integer)
    score_with_time  = db.Column(db.Float)  

    def __init__(self, feed):

        #pull twitter media and picture
        if unicode('media') in feed['entities'].keys():
            self.picture = feed['entities']['media'][0]['media_url']
        
        if self.bool_url_exists(feed):

            try:
                r = requests.get(feed['entities']['urls'][0]['expanded_url'])
                self.link = r.url
            except:
                self.link = feed['entities']['urls'][0]['expanded_url']

            #grab page text
            try:
                self.page_text = r.text
            except:
                self.page_text = "Error grabbing page"



            #get instagram
            if ('http://instagr' in self.link):
                try:
                    soup = BeautifulSoup(self.page_text)
                    a = soup.findAll(attrs={"property":"og:image"})[0]['content']
                    #a = soup.find(id='media_photo').findAll('img')[0]['src']
                    self.picture = a
                except:
                    self.picture = unicode("")
            
            if [image_exists for image_exists in ['.gif', '.jpeg', 'jpg', '.png'] if image_exists in self.link]:
                self.picture = self.link
            

            #get twitpic
            if ('twitpic' in self.link):
                soup = BeautifulSoup(self.page_text)
                a = soup.findAll(attrs={"name":"twitter:image"})[0]['value']
                self.picture = a
            
            #get yfrog
            if ('yfrog' in self.link):
                soup = BeautifulSoup(self.page_text)
                a = soup.findAll(attrs={"property":"og:image"})[0]['content']
                self.picture = a

            #grab main url
            home = urlparse.urlsplit(self.link)
            self.main_url = home.netloc

        #defaults for link, page_text, main_url and main_url
        if not self.bool_url_exists(feed):
            self.link          = unicode("")
            self.page_text     = unicode("")
            self.main_url      = unicode("")
        if not self.picture:
            self.picture       = unicode("")


        self.tweet            = self.json_to_dict(feed)
        self.screen_name      = feed['user']['screen_name']
        self.name             = feed['user']['name']
        self.user_id_str      = feed['user']['id_str'] 
        self.user_id          = feed['user']['id']
        self.user_created_at  = feed['user']['created_at']
        self.user_following   = feed['user']['friends_count']
        self.user_followers   = feed['user']['followers_count']
        self.user_url         = feed['user']['url']
        self.statuses_count   = feed['user']['statuses_count']
        self.profile_picture  = feed['user']['profile_image_url_https']
        self.retweet_count    = feed['retweet_count']
        self.tweet_created_at = feed['created_at']
        self.tweet_id         = feed['id']
        self.text             = self.grab_text(feed)
        self.retweeted        = feed['retweeted'] 
        self.date             = datetime.utcnow()
        self.url_exists       = self.bool_url_exists(feed)
        self.headline         = self.pull_headline(self.page_text)


        self.average_rt_count = 1.0
        self.std_deviation    = 1.0
        self.std_dev_sigma    = .25
        self.score            = 0.5
        self.score_with_time  = 0.5
        
        

    def __repr__(self):
        return "<Tweet by %r>" % self.screen_name

    def json_to_dict(self, dct):
        tweet_str = json.dumps(dct)
        return tweet_str
    
    def grab_text(self, tfeed):
        text = tfeed['text']
        split_text = text.split(' ')
        text_no_tco = ' '.join([x for x in split_text if 'http://t.co' not in x])
        return text_no_tco
    

    def bool_url_exists(self, x):
        if len(x['entities']['urls']) == 0:
            return bool(0)
        else: return bool(1)

    def pull_headline(self, page_text):
        h = HTMLParser.HTMLParser()

        try:
            soup = BeautifulSoup(page_text)
        except:
            soup = BeautifulSoup('')

        if soup.findAll('title'):
            title = soup.find('title')
            content = title.renderContents()
            decode = content.decode("utf-8")
            unicode_text = h.unescape(decode)
            clean_up_0 = self.remove_separator_and_extra_content(unicode_text, " - ")
            #add self 
            clean_up_1 = self.remove_separator_and_extra_content(clean_up_0, " \| ") 
            clean_up_2 = self.remove_separator_and_extra_content(clean_up_1, " \// ")
            #add self
            return clean_up_2
        else: 
            return self.text

    def remove_separator_and_extra_content(self, content, separator): 
        dash = re.findall(separator, content)
        split_content = re.split(separator, content)
        if len(dash) > 0 and len(split_content[0] + split_content[1]) > 30:
            a = split_content[0]
            b = a.lstrip()
            c = b.rstrip()
            return c
        elif len(dash) > 0 and len(split_content[0] + split_content[1]) < 30:
            if separator == " \| ":
                separator = " | "
            a = split_content[0] + unicode(separator) + split_content[1]
            b = a.lstrip()
            c = b.rstrip()
            return c
        else: 
            a = content.lstrip()
            b = a.rstrip()
            return b











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
                db.session.add(tweet)
    db.session.commit()
    print "update successful"



# STILL NOT GOOD ENOUGH. FASTE FASTER FASTER

def update_averages_and_std_deviation(tweets_in_db):
    """Includes retweets of all tweets. Should it be only links?"""
    """tweets_in_db == Tweet.query.all()"""

    already_updated = [] #holds user_id of updated averages

    link_counter = links_number_of_times(tweets_in_db)

    for z in tweets_in_db:
        updating = z.user_id
        if updating not in already_updated:
            
            user = Tweet.query.filter_by(user_id=z.user_id).all()
            retweet_counts = [y.retweet_count for y in user]
            
            
            # average retweet count of user_id
            average = sum(retweet_counts)/len(retweet_counts)
            calculate = sum([pow((g-average), 2) for g in retweet_counts])
            standard_deviation = math.sqrt(calculate/len(retweet_counts))
            Tweet.query.filter_by(user_id=z.user_id).update(dict(average_rt_count=average, std_deviation=standard_deviation))
            db.session.commit()

            for x in user:
                if tweet_age_in_hours(x) < 1680:

                    if standard_deviation != 0:
                        x.std_dev_sigma    = (x.retweet_count - average)/standard_deviation
                    if len(retweet_counts) < 30 and x.std_dev_sigma > 3:
                        x.std_dev_sigma = 3.0

                    if len(retweet_counts) < 5:
                        x.std_dev_sigma = 0
                #ok
                    tweet_hour_age = tweet_age_in_hours(x)

                    number_of_times_retweeted = times_appears_in_stream(x.link, link_counter)

                    points = (10*(x.std_dev_sigma))*number_of_times_retweeted
                    score_with_time = hacker_news(points, tweet_hour_age)

                    x.score = round(points)
                    x.score_with_time = score_with_time
                    db.session.commit()
            
        
        already_updated.append(updating)
                             








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
                    

def tweet_age_in_hours(Tweet):

    created_at = Tweet.date
    right_now = datetime.utcnow()
    tweet_age = right_now - created_at
    age_in_hours = (tweet_age.days)*24 + tweet_age.seconds/3600
    return age_in_hours

def tweets_age_for_view(Tweets):
    list_of_tweet_age = []
    
    for tweet in Tweets:
        age_in_hours = tweet_age_in_hours(tweet)
        if age_in_hours > 24:
            days = age_in_hours/24
            list_of_tweet_age.append((str(days) + " days ago"))
        else:
            list_of_tweet_age.append((str(age_in_hours) + " hours ago"))
    return list_of_tweet_age


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

if __name__ == '__main__':
    # test local db - app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
