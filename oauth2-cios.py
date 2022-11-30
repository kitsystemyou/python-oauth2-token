from requests_oauthlib import OAuth2Session
import os
import base64
import re
import hashlib
import requests
import yaml

from bottle import get, request, route, redirect, template, run
from requests.auth import HTTPBasicAuth

PORT = 8000


with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    API_KEY = config['api_key']
    API_KEY_SECRET = config['api_key_secret']

redirect_url = "http://localhost:8000/oauth2/authorize"
authorization_base_url = "https://auth.pre.cios.dev/connect/authorize"
access_token_endpoint_url = "https://auth.pre.cios.dev/connect/token"


scope = ['file_storage.read', 'user.profile', 'corporation.read']


code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

oauth2_session = OAuth2Session(client_id=API_KEY, scope=scope, redirect_uri=redirect_url)

authorization_url, state = oauth2_session.authorization_url(authorization_base_url, code_challenge=code_challenge, code_challenge_method="S256")


token_url = "https://auth.pre.cios.dev/connect/token"
auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)

print("start!")


@route("/")
def index():
    pf = 'CIOS'
    return template('index', pf=pf)


@get('/oauth2/authorize')
def get_token():
    auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)
    print("request.url: ", request.url)
    print(request.url.replace('http', 'https'))
    url = request.url.replace('http', 'https')
    authorization_response = url

    token = oauth2_session.fetch_token(
        token_url=token_url,
        authorization_response=authorization_response,
        auth=auth,
        client_id=API_KEY,
        include_client_id=True,
        code_verifier=code_verifier,
    )
    print(token)
    access = token["access_token"]

    params = {"user.fields": "created_at,description"}
    headers = {
        "Authorization": "Bearer {}".format(access)
    }
    url = "https://accounts.preapis.cios.dev/v2/me"
    print("headers", headers, "params", params)
    response = requests.request("GET", url, headers=headers)  # params=params
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    print(response.json())
    name = response.json()['name']
    email = response.json()['email']

    return template('result', name=name, email=email, token=access)


@get('/oauth/connect')
def request_token():
    return redirect(authorization_url)


run(host='localhost', port=PORT, debug=True, reloader=False)
