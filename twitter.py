from requests_oauthlib import OAuth1Session
import webbrowser
from bottle import run, get, request
# import time

PORT = 8000
API_KEY = "jWyJTNBL2kE3BHaO4cK1rFnKV"
API_KEY_SECRET = "3V4gzH35OggELo3i6ALGbwKi1EJV4uGOM8yuzy6O4fzfiiLGAv"


callback_url = "http://localhost:8000/"
request_endpoint_url = "https://api.twitter.com/oauth/request_token"
authenticate_url = "https://api.twitter.com/oauth/authenticate"
access_endpoint_url = "https://api.twitter.com/oauth/access_token"

print("start process")

session_req = OAuth1Session(API_KEY, API_KEY_SECRET)
response_req = session_req.post(
    request_endpoint_url, params={
        "oauth_callback": callback_url})
response_req_text = response_req.text

oauth_token_kvstr = response_req_text.split("&")
token_dict = {x.split("=")[0]: x.split("=")[1] for x in oauth_token_kvstr}
print(token_dict)
oauth_token = token_dict["oauth_token"]
auth_url = f"{authenticate_url}?oauth_token={oauth_token}"
print("認証URL:", auth_url)

error = webbrowser.open(auth_url)
print("☕ browser error ", error)
# oauth_verifier = input("OAuth Verifierを入力してください> ")

print("start server")


@get('/')  # redirected url
def get_token():
    print("🍌 Redirected")
    oauth_verifier = request.query.oauth_verifier
    print("🍎", oauth_token, oauth_verifier)

    # time.sleep(10)
    session_acc = OAuth1Session(
        API_KEY,
        API_KEY_SECRET,
        oauth_token,
        oauth_verifier)
    response_acc = session_acc.post(
        access_endpoint_url, params={
            "oauth_verifier": oauth_verifier})
    response_acc_text = response_acc.text
    print("🍇", response_acc_text)
    print(response_acc.status_code)

    access_token_kvstr = response_acc_text.split("&")
    acc_token_dict = {x.split("=")[0]: x.split("=")[1]
                      for x in access_token_kvstr}
    access_token = acc_token_dict["oauth_token"]
    access_token_secret = acc_token_dict["oauth_token_secret"]

    print("🌟")
    print("Access Token       :", access_token)
    print("Access Token Secret:", access_token_secret)
    print("User ID            :", acc_token_dict["user_id"])
    print("Screen Name        :", acc_token_dict["screen_name"])
    return {"status": "ok"}


run(host='localhost', port=PORT, debug=True, reloader=False)
