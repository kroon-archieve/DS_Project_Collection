import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

### Credential
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ACCESSS_TOKEN = os.getenv('ACCESSS_TOKEN')
ACCESSS_TOKEN_SECRET = os.getenv('ACCESSS_TOKEN_SECRET')

# Connect to Tweepy
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESSS_TOKEN, ACCESSS_TOKEN_SECRET)

api = tweepy.API(auth)
