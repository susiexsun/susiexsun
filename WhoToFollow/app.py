from flask import Flask, request, render_template
app = Flask(__name__)
import retweet_predict as rp
import cPickle as pickle
from pymongo import MongoClient
from collections import defaultdict

@app.route('/')
def whotofollow(): 
    return render_template('whotofollow.html')

@app.route('/recommend', methods=['POST'])
def screen_name():
    text = str(request.form['screen_name'])
    print "screen_name: ", text
    data = rp.get_data(text)
    print "data: ", data
    output = rp.predict(data, vect, text)

    client = MongoClient()
    twitter = client['twitter']
    new = twitter['new']

    tweet_output = defaultdict(list)
    handle_output = {}

    for screen_name in output:
        docs = new.find({'user.screen_name': screen_name}).limit(3)
        for doc in docs: 
            the_id = doc.get('id')
            the_handle = doc.get('user').get('screen_name')
            tweet_output[the_handle].append("https://twitter.com/jack/status/%s" % the_id)
            handle_output[the_handle] = "https://twitter.com/%s" %the_handle
    

    return render_template('results.html', tweet_output=tweet_output, handle_output=handle_output)


if __name__ == '__main__':
    with open('data/retweet_vectorizer.pkl') as f: 
        vect = pickle.load(f)
        print 'vect loaded'
    app.run(host='0.0.0.0', port=8080, debug=True)