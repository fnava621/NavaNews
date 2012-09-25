from twython import Twython
from nava_rank import db
from nava_rank import Tweet
import math, sched, time, collections, re
from threading import Timer
from datetime import datetime, timedelta 
from nava_rank import tavorite, tweet_age_in_hours, tweets_age_for_view, following



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


def links_number_of_times():
    Tweets = Tweet.query.all()
    tweets = [x for x in Tweets if x.url_exists] 
    links = filter_for_double_links(tweets)
    cnt = collections.Counter(links).most_common(100)
    return cnt


#link_counter = [(u'http://cdixon.org/2012/09/16/facebooks-embedded-option/', 5), (u'http://blog.uber.com/2012/09/20/here-we-go-again-dc-taxi-commission-proposes-new-rules-to-shut-down-uber/', 4), (u'http://www.kickstarter.com/projects/limemouse/lifx-the-light-bulb-reinvented', 4), (u'http://www.nytimes.com/', 4), (u'http://pandomonthlyjonahperetti.eventbrite.com/', 3), (u'http://www.kalzumeus.com/2012/09/17/ramit-sethi-and-patrick-mckenzie-on-getting-your-first-consulting-client/', 3), (u'https://blog.wealthfront.com/startup-employee-equity-compensation/', 3), (u'http://redeye.firstround.com/2012/09/the-dorm-room-fund.html', 3), (u'http://gigaom.com/2012/09/20/us-and-stack-exchange-launch-crowdsourced-patent-process/', 3), (u'http://fosslien.com/startup/', 3), (u'http://bijansabet.com/post/31918354877/behind-closed-doors', 3), (u'http://daslee.me/why-i-never-started-my-own-company', 3), (u'http://bits.blogs.nytimes.com/2012/09/16/disruptions-let-silicon-valley-eat-ramen-noodles/', 3), (u'http://www.bothsidesofthetable.com/2012/09/22/is-going-for-rapid-growth-always-good-arent-startups-so-much-more/', 3), (u'http://www.nytimes.com/2012/09/18/opinion/brooks-thurston-howell-romney.html?_r=1', 3), (u'http://steveblank.com/2012/09/21/why-too-many-startups-er-suck/', 2), (u'http://www.wired.com/business/2012/09/mf-mary-meeker/all/', 2), (u'http://techcrunch.com/2012/09/18/iphone-5-review/', 2), (u'http://www.avc.com/a_vc/2012/09/cross-network-utility-and-networks.html', 2), (u'http://pandodaily.com/2012/09/20/21-jonah-peretti-quotes-that-will-restore-your-faith-in-buzzfeed/', 2), (u'http://learning.blogs.nytimes.com/2012/09/20/writing-rules-advice-from-the-new-york-times-on-writing-well/', 2), (u'http://www.vanityfair.com/politics/2012/10/michael-lewis-profile-barack-obama', 2), (u'http://coudal.com/', 2), (u'http://apiblog.youtube.com/2012/09/the-youtube-api-on-stack-overflow.html', 2), (u'http://twitter.yfrog.com/oc7ijhuj', 2), (u'http://www.grantland.com/blog/the-triangle/post/_/id/37239/b-s-report-cousin-sal-16', 2), (u'http://www.businessinsider.com/newspaper-advertising-collapse-2012-9', 2), (u'http://www.thedailybeast.com/articles/2012/09/20/dc-taxi-commission-apparently-still-wants-uber-dead.html', 2), (u'http://gigaom.com/2012/09/22/silicon-valley-is-stupid-which-is-why-it-works/', 2), (u'http://www.markboulton.co.uk/journal/comments/five-simple-steps-to-better-typography', 2), (u'http://qz.com/', 2), (u'http://www.grantland.com/blog/hollywood-prospectus/post/_/id/57984/grantland-exclusive-battle-of-the-seasons-preview-clip', 2), (u'http://versiononeventures.com/the-only-2-ways-to-build-a-100-million-business/', 2), (u'http://www.reddit.com/r/IAmA/comments/107ryg/hello_its_aziz_ansari_again_ama/', 2), (u'http://www.ign.com/articles/2012/09/19/patterns-could-be-the-next-minecraft', 2), (u'http://codeforamerica.theresumator.com/apply/R73VZn/NYC-Program-Manager.html', 2), (u'http://www.cbsnews.com/8301-501465_162-57514905-501465/jetblue-to-offer-free-in-flight-wi-fi-in-2013/', 2), (u'http://pandodaily.com/2012/09/17/wow-anonymous-donor-buys-out-rest-of-jonah-peretti-tickets-on-one-condition/', 2), (u'http://whitneyhess.com/blog/2012/09/13/if-vcs-understood-ux/', 2), (u'http://instagram.com/p/PzqaXTAR-e/', 2), (u'http://www.grantland.com/story/_/id/8377762/the-mailbag-week-2-combo-platter', 2), (u'http://www.businessinsider.com/sequoia-capital-jim-goetz-on-enterprise-startups-2012-9?utm_source=twbutton&utm_medium=social&utm_campaign=enterprise', 2), (u'http://www.startuplessonslearned.com/2012/09/workshop-lean-entrepreneur-with-brant.html', 2), (u'http://twitpic.com/avrlm4', 2), (u'http://www.brainpickings.org/index.php/2012/07/25/susan-sontag-on-writing/', 2), (u'http://www.brainpickings.org/index.php/2012/06/15/fatherly-advice-letters/', 2), (u'http://blog.stackoverflow.com/2012/09/askpatents-com-a-stack-exchange-to-prevent-bad-patents/', 2), (u'http://patents.stackexchange.com/', 2), (u'http://ecorner.stanford.edu/authorMaterialInfo.html?mid=2988&utm_source=buffer&buffer_share=5041e', 2), (u'http://www.buzzfeed.com/txblacklabel/true-love-in-pictures-only-28m7', 2), (u'http://pandodaily.com/2012/09/18/how-much-should-startup-employees-earn-wealthfront-tells-us-with-a-clever-tool/', 2), (u'http://exp.lore.com/post/31593652196/in-his-fantastic-science-off-the-sphere-series', 2), (u'http://www.farnamstreetblog.com/2012/09/the-untrained-mind-will-usually-take-the-path-of-least-resistance/', 2), (u'http://twitter.com/pkedrosky/status/250386012105232384/photo/1', 2), (u'http://www.guardian.co.uk/commentisfree/oliver-burkemans-blog/2012/sep/13/romney-ryan-election-bullshit?INTCMP=SRCH', 2), (u'http://techcrunch.com/2012/09/15/being-more-accessible/', 2), (u'http://www.makerbot.com/blog/2012/09/19/a-whole-new-makerbot-introducing-replicator-2-desktop-3d-printer/', 2), (u'http://pandodaily.com/2012/09/19/stumbleupons-new-iphone-app-proves-the-company-is-ready-for-all-things-social-mobile-and-local/', 2), (u'http://www.youtube.com/watch?feature=player_embedded&v=XoMN-zg7r3M', 2), (u'http://venturebeat.com/2012/09/19/stumbleupon-for-ios/', 2), (u'http://pandodaily.com/2012/09/18/stop-sto/', 2), (u'http://www.theverge.com/2012/9/17/3322854/google-startup-mergers-acquisitions-failure-is-a-feature', 2), (u'http://venturebeat.com/2012/09/19/gnip-twitter-historical/', 2), (u'http://www.grantland.com/blog/the-triangle/post/_/id/37913/b-s-report-cousin-sal-17', 2), (u'http://www.parc.com/event/1754/innovation.html', 2), (u'http://uncrunched.com/2012/09/24/crunchfund-1-party-at-sf-creamery/', 2), (u'http://www.entrepreneur.com/video/224019', 2), (u'http://pandodaily.com/2012/09/20/the-new-middle-east-women-at-the-center-of-a-startup-ecosystem/', 2), (u'https://plus.google.com/+Scobleizer/posts/Cko5BoHHhNs', 2), (u'http://gawker.com/5945967/romney-doesnt-know-why-airplane-windows-wont-open-calls-the-closed-window-policy-a-real-problem', 2), (u'http://www.grantland.com/story/_/id/8396297/is-new-york-knicks-shooting-guard-jr-smith-misguided-just-misunderstood', 2), (u'http://makerbot.com/', 2), (u'http://www.themorningnews.org/article/the-city-of-right-angles', 2), (u'http://www.grantland.com/blog/the-triangle/post/_/id/37634/the-sports-guys-thursday-nfl-pick-heres-your-skunk-of-the-week', 2), (u'http://www.motherjones.com/mojo/2012/09/romney-secret-video-marc-leder-sex-parties', 2), (u'http://www.grantland.com/story/_/id/8388994/chavez-martinez-canelo-josesito-state-boxing', 2), (u'http://paulgraham.com/growth.html', 2), (u'http://www.grantland.com/story/_/id/8391106/lane-kiffin-usc-was-supposed-challenge-national-title-season-ran-stanford-again', 2), (u'http://www.nytimes.com/2012/09/18/opinion/brooks-thurston-howell-romney.html?_r=4&smid=tw-share', 2), (u'http://jayrosenkrantz.blogspot.com/2012/09/boom-documentary-blog.html', 2), (u'http://www.nytimes.com/2012/09/16/opinion/sunday/kristof-the-foreign-relations-fumbler.html?_r=1&smid=tw-share', 2), (u'http://farmhouse.la/conf/3', 2), (u'http://www.pokerstars.com/wcoop/radio/', 2), (u'http://www.grantland.com/blog/hollywood-prospectus/post/_/id/58055/dmx-vs-the-computer-an-analysis', 2), (u'http://itunes.apple.com/us/app/tweetbot-for-twitter-ipad/id498801050?mt=8', 2), (u'http://www.leanstartupconf.com/sponsors', 2), (u'http://fab.com/inspiration/baconlube', 1), (u'http://punchlinecomedyclub.com/event/1C004918CD2A72E1', 1), (u'http://exp.lore.com/post/31501860266/in-1965-salvador-dali-designed-a-bizarre-line-of', 1), (u'http://twitter.yfrog.com/nzxsjkaj', 1), (u'https://speakerdeck.com/u/pydanny/p/extreme-zen-of-pytho', 1), (u'http://www.grantland.com/blog/hollywood-prospectus/post/_/id/57899/tom-scharpling-qa', 1), (u'http://allthingsd.com/20120918/not-ready-for-iphone-5-upgrade-offers-some-new-tricks/?mod=tweet', 1), (u'http://www.strava.com/rides/22231865', 1), (u'http://www.waywire.com/v/5a7b187742b5117d94ad4459b55b2a9e', 1), (u'http://amandapeyton.com/blog/2012/09/like-the-supercomputer-it-is/', 1), (u'http://www.latimes.com/health/la-me-english-only-20120918,0,7143293.story', 1), (u'http://5by5.tv/live', 1), (u'https://twitter.com/pulsepad', 1), (u'http://events.r20.constantcontact.com/register/event?oeidk=a07e6bmkal49fa2f845&llr=zy5crzdab', 1)]


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

link_counter = links_number_of_times()

# STILL NOT GOOD ENOUGH. FASTE FASTER FASTER

def update_averages_and_std_deviation():
    
    """Includes retweets of all tweets. Should it be only links?"""
    """tweets_in_db == Tweet.query.all()"""

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
