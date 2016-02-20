from sklearn.metrics.pairwise import linear_kernel
from pymongo import MongoClient
import sys
import numpy as np
from collections import Counter, defaultdict
import tweepy
from tweepy import OAuthHandler
from retweet_model import run_model, most_retweets
import cPickle as pickle

def get_data(sn): 

	consumer_key = "HXJfoPTVxH6Iqqzv4nY5SlYgO"
	consumer_secret = "7LfAfz2a0LmH4dH46X4mUXSH6RTVmiS9zE1kgcBkw5NPirEkJ1"
	access_token = "34633790-ENRADvdaiEsSEhudIrNRQrxZPrPcb4hMLPupf5seb"
	access_token_secret = "hCKKwx5FyzpspWvnVr1wv4sU7JHlUNwVdJPPFrcL34wT3"

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

	client = MongoClient()
	twitter = client['twitter']
	new = twitter['new']

	user_tweets = api.user_timeline(sn, count=30)
	new.insert_many(user_tweets)

	docs = new.find({'user.screen_name': sn})
	data = []
	for tweet in docs:
		tweet_text = tweet.get('text').encode('utf8', 'ignore')
		data.append(tweet_text)

	return data


def predict(data, vect, sn): 
	vector = vect.transform(data)

	# get list of the ids of the retweeted people
	most_retweet_ids = run_model(sn)

	client = MongoClient()
	twitter = client['twitter']
	new = twitter['new']

	handle_tweet_dict = defaultdict(list)
	id_handle_dict = defaultdict()

	for an_id in most_retweet_ids:	 
		docs = new.find({'user.id': an_id})
		for doc in docs: 
			tweet = doc.get('text').encode('utf8', 'ignore')
			user_id = doc.get('user').get('id')
			handle = doc.get('user').get('screen_name')
			handle_tweet_dict[handle].append(tweet)
			id_handle_dict[user_id] = handle


	tweet_list = []
	handle_list = []

	for k, v in handle_tweet_dict.iteritems(): 
		tweet_list.extend(v)
		handle_list.extend([k]*len(v))

	vector = vect.transform(data)
	new_word_counts = vect.transform(tweet_list)

	result_matrix = linear_kernel(vector, new_word_counts)
	
	indices_of_tweets = []

	# For each tweet by the client, find the 30 most similar tweets
	# This list may include tweets by the client
	for row in result_matrix: 
		indices = row.argsort()[:][::-1]
		indices_of_tweets.append(indices[:31])


	# Return the ids of persons that tweeted each of the 30 most similar tweets
	handle_array = np.array(handle_list)
	persons_per_tweet = []

	for row in indices_of_tweets: 
		persons_per_tweet.append(handle_array[row])

	# Count up how many times each person shows up. 
	# Same weighting is given to people who have many tweets similar to one client tweet
	# and a tweet that matches a high number of client tweets.
	persons_counter = Counter()

	for row in persons_per_tweet: 
		persons_counter.update(row)

	# return the top 25 people in this list
	top_people_and_count = persons_counter.most_common(10)

	top_people = [tup[0] for tup in top_people_and_count if tup[0] != sn]

	return top_people
