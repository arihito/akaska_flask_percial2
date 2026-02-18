import os
import stripe
from dotenv import load_dotenv

load_dotenv()

def init_stripe(app):
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
