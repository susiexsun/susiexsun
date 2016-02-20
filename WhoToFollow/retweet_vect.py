import numpy as np
from pymongo import MongoClient
from collections import OrderedDict, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import cPickle as pickle

class Model1(object): 
	def __init__(self): 
		self.handle_tweet_dict = None
		self.vect = None
		self.word_counts = None
		self.id_handle_dict = None

	def create_conn_and_database(self): 
		''' Connects to MongoDB database and pulls data for model. 
		This only needs to be run once per model.'''

		client = MongoClient()
		whotofollow = client['whotofollow']
		new = whotofollow['new']
		text_and_id = new.find({}, {'user.id':1, 'user.screen_name':1, 'text':1, '_id':0})


		processed_whotofollow = client['processed_whotofollow']
		graph_model = processed_whotofollow['graph_model']
		graph_model.insert(text_and_id)


	def run_model(self):
		''' Turns data into a usable format for the TfidfVectorizer 
		
		INPUT: MongoDB data with 1 Mongo Document per tweet
		
		OUTPUT: Updates self.dict with OrderedDict. OrderedDict has 1 
		key per person, and the text is 1 long string with all of the tweets.
		'''

		client = MongoClient()
		processed_whotofollow = client['processed_whotofollow']
		graph_model = processed_whotofollow['graph_model']

		docs = graph_model.find()
		handle_tweet_dict = defaultdict(list)
		id_handle_dict = defaultdict(list)

		for doc in docs: 
			tweet = doc.get('text').encode('utf8', 'ignore')
			user_id = doc.get('user').get('id')
			handle = doc.get('user').get('screen_name')
			handle_tweet_dict[handle].append(tweet)
			id_handle_dict[user_id] = handle

		model_input = [x for sublist in handle_tweet_dict.values() for x in sublist]

		vect = TfidfVectorizer()
		word_counts = vect.fit_transform(model_input)

		self.handle_tweet_dict = handle_tweet_dict
		self.vect = vect
		self.word_counts = word_counts
		self.id_handle_dict = id_handle_dict


if __name__ == '__main__':
	model = Model1()
	model.create_conn_and_database()
	model.run_model()
	with open('data/retweet_handle_tweet_dict.pkl', 'w') as f: 
		pickle.dump(model.handle_tweet_dict, f)
	with open('data/retweet_vectorizer.pkl', 'w') as f: 
		pickle.dump(model.vect, f)
	with open('data/retweet_word_counts.pkl', 'w') as f: 
		pickle.dump(model.word_counts, f)
	with open('data/retweet_id_handle_dict.pkl', 'w') as f: 
		pickle.dump(model.id_handle_dict, f)

	