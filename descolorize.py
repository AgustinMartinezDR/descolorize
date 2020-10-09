import tweepy
import os
import requests
from os import environ
from decouple import config
from io import BytesIO
from flask import Flask, request
from PIL import Image, ImageOps

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_TOKEN = environ['ACCESS_TOKEN']
ACCESS_SECRET = environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(config("CONSUMER_KEY"), config("CONSUMER_SECRET"))
auth.set_access_token(config("ACCESS_TOKEN"), config("ACCESS_SECRET"))
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

def descolorize(filename):
	img = Image.open(filename)
	grayScale = img.convert("LA")
	#with open('grayScale.png', 'wb') as out:
	grayScale.save('grayScale.png')


def tweet_image(url, username, status_id):
	filename = 'temp.png'
	response = requests.get(url, stream=True)
	if response.status_code == 200:
		#print(response.text)
		print(response.url)
		#print(response.raw)
		response.raw.decode_content = True
		i = Image.open(response.raw)
		i.save(filename)
		descolorize(filename)
		api.update_with_media('grayScale.png', status=f'@{username} Here is the picture in a gray scale', in_reply_to_status_id=status_id)
	else:
		print("unable to download image")


class TweetsListener(tweepy.StreamListener):
	def on_connect(self):
		print("Estoy conectado!")

	def on_status(self, status):
		print(status.text)
		username = status.user.screen_name
		status_id = status.id

		if 'media' in status.entities:
			for image in status.entities['media']:
				tweet_image(image['media_url'], username, status_id)

	def on_error(self, status_code):
		print("Error", status_code)


app = Flask(__name__)
with app.test_request_context():

	stream = TweetsListener()
	streamingApi = tweepy.Stream(auth = api.auth, listener = stream)
	streamingApi.filter(
		track=["@descolorize"]
	)
