import os

from dotenv import load_dotenv
load_dotenv()

class DefaultConfig(object):
  DEBUG = False
  TESTING = False

  BUSINESS_CLIENT = os.environ['BUSINESS_CLIENT']