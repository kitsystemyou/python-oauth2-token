from requests_oauthlib import OAuth2Session
import os
import base64
import re
import hashlib
import requests

from bottle import run, get, request, redirect
from requests.auth import HTTPBasicAuth

PORT = 8000
API_KEY = "WXRqczNfRGxBbkdIUmd1ZFd4N046MTpjaQ"
API_KEY_SECRET = "yNEA3Vz7ICuDH_Fm4kRohSO2YrePVnSGuG-tmPSQl7-RmgG6sD"


callback_url = "http://localhost:8000/"

authorization_base_url = "https://twitter.com/i/oauth2/authorize"
access_token_endpoint_url = "https://api.twitter.com/oauth/access_token"


scope = ['tweet.read', 'users.read']


code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

twitter = OAuth2Session(client_id=API_KEY, scope=scope, redirect_uri=callback_url)

authorization_url, state = twitter.authorization_url(authorization_base_url, code_challenge=code_challenge, code_challenge_method="S256")


token_url = "https://api.twitter.com/2/oauth2/token"
auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)


print("start!")


@get('/')
def get_token():
    auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)
    print("request.url: ", request.url)
    print(request.url.replace('http', 'https'))
    url = request.url.replace('http', 'https')
    authorization_response = url

    token = twitter.fetch_token(
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
        "Authorization": "Bearer {}".format(access),
        "User-Agent": "auth_test",
    }
    url = "https://api.twitter.com/2/users/me"
    response = requests.request("GET", url, params=params, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    print(response.json())
    data = response.json()['data']
    name = data['name']
    desc = data['description']

    print("🌟")
    return f"""
        <body>
            <center>
            <h1>Authentication Succeed!</h1>
            <h2> ユーザー名: {name}</h2>
            <h2> プロフィール(description): {desc}</h2>
            </center>
        </body>
        """


@get('/oauth/connect')
def request_token():
    return redirect(authorization_url)


run(host='localhost', port=PORT, debug=True, reloader=False)
