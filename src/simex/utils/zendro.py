import os
import requests

from simex.settings import SIPECAM_ZENDRO_GQL_URL, SIPECAM_ZENDRO_GQL_USER, \
SIPECAM_ZENDRO_GQL_PASSWORD

def get_credentials():
    return {
            "username": SIPECAM_ZENDRO_GQL_USER,
            "password": SIPECAM_ZENDRO_GQL_PASSWORD,
           }
def get_zendro_url_for_login():
    return os.path.join(SIPECAM_ZENDRO_GQL_URL,"login")

def get_zendro_url_for_gql():
    return os.path.join(SIPECAM_ZENDRO_GQL_URL, "graphql")

def get_token():
    """
    Get a token that allows to make zendro queries.
    
    Returns: 
        token (str):  token.
    """  
    login = requests.post(get_zendro_url_for_login(),
                          data=get_credentials())
    
    if login.status_code == 200:
        return login.json()['token']
    else:
        print("bad credentials in .simex_env")
        return None