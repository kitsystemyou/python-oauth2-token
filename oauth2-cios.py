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

# TODO: Add config.yaml
redirect_url = "http://localhost:8000/oauth2/authorize"
authorization_base_url = "https://auth.pre.cios.dev/connect/authorize"
token_url = "https://auth.pre.cios.dev/connect/token"
scope = ['file_storage.read', 'user.profile', 'corporation.read', 'corporation.user.read', 'group.read']

# NOTE: OPTIONNAL. for PKCE
code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

oauth2_session = OAuth2Session(client_id=API_KEY, scope=scope, redirect_uri=redirect_url)

authorization_url, state = oauth2_session.authorization_url(authorization_base_url, code_challenge=code_challenge, code_challenge_method="S256")


auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)

print("start!")


def get_group_members(headers, groupID):
    ggmurl = f"https://accounts.preapis.cios.dev/v2/groups/{groupID}/members"
    ggmres = requests.request("GET", ggmurl, headers=headers)
    if ggmres.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(ggmres.status_code, ggmres.text)
        )
    return ggmres.json()


@route("/")
def index():
    pf = 'CIOS'
    return template('index', pf=pf)


@get('/oauth2/authorize')
def get_token():
    print("API_KEY:", API_KEY)
    print("API_KEY_SECRET:", API_KEY_SECRET)
    auth = HTTPBasicAuth(API_KEY, API_KEY_SECRET)
    url = request.url.replace('http', 'https')  # NOTE: for local
    authorization_response = url

    token = oauth2_session.fetch_token(
        token_url=token_url,
        authorization_response=authorization_response,
        auth=auth,
        include_client_id=True,
        code_verifier=code_verifier,
    )
    access = token["access_token"]

    headers = {
        "Authorization": f"Bearer {access}"
    }
    
    # Get My Profie API
    url = "https://accounts.preapis.cios.dev/v2/me"
    getmyprofile_response = requests.request("GET", url, headers=headers)
    if getmyprofile_response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(getmyprofile_response.status_code, getmyprofile_response.text)
        )
    userprofile = getmyprofile_response.json()
    name = userprofile['name']
    email = userprofile['email']
    corpID = userprofile['corporation']['id']
    userID = userprofile['id']
    groups = userprofile['groups']
    
    # Read Corporation User API
    gcuurl = f"https://accounts.preapis.cios.dev/v2/corporations/{corpID}/users/{userID}"
    getcorporationuser_response = requests.request("GET", gcuurl, headers=headers)
    if getcorporationuser_response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(getcorporationuser_response.status_code, getcorporationuser_response.text)
        )
    cuserdata = getcorporationuser_response.json()

    group_info = [get_group_members(headers, x['id']) for x in groups]
    print(group_info)
    group_infoes = [g['members'] for g in group_info]
    return template('result', name=name, email=email, token=access, userprofile=userprofile, cuserdata=cuserdata, group_infoes=group_infoes)


@get('/oauth/connect')
def request_token():
    return redirect(authorization_url)


run(host='0.0.0.0', port=PORT, debug=True, reloader=False)
