import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
import os
from dotenv import load_dotenv

load_dotenv()

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Service functions
def create_link_token():
    """Create a Plaid Link token"""
    request = LinkTokenCreateRequest(
        products=[Products("investments")],
        client_name="Portfolio Tracker",
        country_codes=[CountryCode('US'), CountryCode('CA')],
        language='en',
        user=LinkTokenCreateRequestUser(client_user_id='test-user')
    )
    response = client.link_token_create(request)
    return response['link_token']

def exchange_public_token(public_token: str):
    """Exchange public token for access token"""
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response['access_token']