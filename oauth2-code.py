from requests_oauthlib import OAuth2Session
import os
import base64
import re
import hashlib
import requests
# import webbrowser
from bottle import run, get, request
from requests.auth import HTTPBasicAuth

PORT = 8000
API_KEY = ""
API_KEY_SECRET = ""


callback_url = "https://localhost:8000/"
# request_endpoint_url = "https://api.twitter.com/oauth/request_token"
authorization_base_url = "https://twitter.com/i/oauth2/authorize"
access_token_endpoint_url = "https://api.twitter.com/oauth/access_token"

# 認可リクエスト
scope = ['tweet.read', 'users.read']


code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

twitter = OAuth2Session(client_id=API_KEY, scope=scope, redirect_uri=callback_url)

authorization_url, state = twitter.authorization_url(authorization_base_url, code_challenge=code_challenge, code_challenge_method="S256")

print(authorization_url)
# webbrowser.open(authorization_url)

token_url = "https://api.twitter.com/2/oauth2/token"
auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)

authorization_response = input("authorization response")

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
print(response.text)
print("finish!")


@get('/')  # redirected url
def get_token():
    # クエリパラメータから oauth_verifire 取得
    oauth_verifier = request.query.oauth_verifier
    # アクセストークンリクエスト
    session_acc = OAuth2Session(
        API_KEY,
        API_KEY_SECRET,
        oauth_verifier)
    response_acc = session_acc.post(
        "", params={
            "oauth_verifier": oauth_verifier})
    response_acc_text = response_acc.text
    # レスポンスをパース
    access_token_kvstr = response_acc_text.split("&")
    acc_token_dict = {x.split("=")[0]: x.split("=")[1]
                      for x in access_token_kvstr}
    access_token = acc_token_dict["oauth_token"]
    access_token_secret = acc_token_dict["oauth_token_secret"]
    print(acc_token_dict)

    print("🌟")
    print("Access Token       :", access_token)
    print("Access Token Secret:", access_token_secret)
    return {"status": "ok"}


run(host='localhost', port=PORT, debug=True, reloader=False)
