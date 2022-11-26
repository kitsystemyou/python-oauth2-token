from requests_oauthlib import OAuth1Session
import webbrowser
from bottle import run, get, request

PORT = 8000
API_KEY = ""
API_KEY_SECRET = ""


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
oauth_token = token_dict["oauth_token"]
# 認証URL作成
auth_url = f"{authenticate_url}?oauth_token={oauth_token}"
print("認証URL:", auth_url)

# ブラウザで認証URLを開く(要ブラウザ) または、標準出力に出力される認証URLをブラウザで手動で開く
webbrowser.open(auth_url)
# oauth_verifier = input("OAuth Verifierを入力してください> ")

print("start server")


@get('/')  # redirected url
def get_token():
    # クエリパラメータから oauth_verifire 取得
    oauth_verifier = request.query.oauth_verifier
    # アクセストークンリクエスト
    session_acc = OAuth1Session(
        API_KEY,
        API_KEY_SECRET,
        oauth_token,
        oauth_verifier)
    response_acc = session_acc.post(
        access_endpoint_url, params={
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
    print("User ID            :", acc_token_dict["user_id"])
    print("Screen Name        :", acc_token_dict["screen_name"])
    return {"status": "ok"}


run(host='localhost', port=PORT, debug=True, reloader=False)
