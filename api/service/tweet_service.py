class TweetService:
    def __init__(self, tweet_dao, config):
        self.tweet_dao = tweet_dao
        self.config = config

    def get_timeline(self, user_id):
        return self.tweet_dao.get_timeline(user_id)
    
    def insert_tweet(self, tweet):
        self.tweet_dao.insert_tweet(tweet)