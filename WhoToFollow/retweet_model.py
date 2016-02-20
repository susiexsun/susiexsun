from pymongo import MongoClient
from collections import Counter
from collections import defaultdict
import tweepy
from tweepy import OAuthHandler
import sys


def run_model(sn): 
	client = MongoClient()
	twitter = client['twitter']
	new = twitter['new']

	consumer_key = "HXJfoPTVxH6Iqqzv4nY5SlYgO"
	consumer_secret = "7LfAfz2a0LmH4dH46X4mUXSH6RTVmiS9zE1kgcBkw5NPirEkJ1"
	access_token = "34633790-ENRADvdaiEsSEhudIrNRQrxZPrPcb4hMLPupf5seb"
	access_token_secret = "hCKKwx5FyzpspWvnVr1wv4sU7JHlUNwVdJPPFrcL34wT3"

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

	if new.find_one({'user.screen_name': sn}) is None: 
		try: 
			print 'scraping: ', sn
			user_tweets = api.user_timeline(sn, count=50)
			new.insert_many(user_tweets)
		except: 
			print sys.exc_info()

	# 5 ids. returns list of ids for the most retweeted of friends of target
	try: 
		doc = new.find_one({'user.screen_name': sn})
		an_id = doc.get('user').get('id')
	except: 
		print "No Person By This Name"

	first_gen = most_retweets(an_id)

	# 25 ids. list with top five retweeted of each from generation 1.
	second_dict = defaultdict(list)

	for an_id in first_gen:  
		retweeted = most_retweets(an_id)
		second_dict[an_id].extend(retweeted)


	# 125 ids. list with top five retweeted of each from generation 2. 
	second_gen_list = [x for sublist in second_dict.values() for x in sublist]
	print "second gen list: ", len(second_gen_list)

	third_dict = defaultdict(list)

	for item in second_gen_list: 
			third_dict[item].extend(most_retweets(item))

	third_gen_list = [x for sublist in third_dict.values() for x in sublist]
	print "third gen list: ", len(third_gen_list)

	output = []
	output.extend(first_gen)
	output.extend(second_gen_list)
	output.extend(third_gen_list)

	print len(output)

	return output


def most_retweets(an_id): 
	client = MongoClient()
	twitter = client['twitter']
	new = twitter['new']

	consumer_key = "HXJfoPTVxH6Iqqzv4nY5SlYgO"
	consumer_secret = "7LfAfz2a0LmH4dH46X4mUXSH6RTVmiS9zE1kgcBkw5NPirEkJ1"
	access_token = "34633790-ENRADvdaiEsSEhudIrNRQrxZPrPcb4hMLPupf5seb"
	access_token_secret = "hCKKwx5FyzpspWvnVr1wv4sU7JHlUNwVdJPPFrcL34wT3"

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
	
	my_counter = Counter()

	if new.find_one({'user.id': an_id}) is None: 
		print "scraping: ", an_id
		user_tweets = api.user_timeline(an_id, count=50)
		new.insert_many(user_tweets)

	docs = new.find({'user.id': an_id})		
	for doc in docs:
		if doc.get('text')[:2] == "RT":
			try: 
				retweet_handle = doc.get('retweeted_status').get('user').get('id')
				my_counter[retweet_handle] += 1
			except:
				pass
		elif doc.get('retweeted') == True: 
			try: 
				retweet_handle = doc.get('retweeted_status').get('user').get('id')
				my_counter[retweet_handle] += retweet_handle
			except: 
				pass

	top_5 = [tup[0] for tup in my_counter.most_common(5)]

	return top_5

if __name__ == '__main__':
	print run_model('justinbieber')

