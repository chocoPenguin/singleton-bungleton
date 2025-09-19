import requests
from config import settings

# Dataverse OAuth2 access token 필요
DATAVERSE_API_URL = settings.dataverse_api_url
ACCESS_TOKEN = settings.dataverse_access_token 

def send_to_dataverse(user_id: int, question_set_id: int, email: str, link: str):
    access_token = get_dataverse_access_token()  # 🔑 매번 최신 토큰 받아오기
    url = f"{settings.dataverse_api_url}/api/data/v9.2/cra4a_quiz_assignments"

    data = {
        "cra4a_user_id": user_id,
        "cra4a_question_set_id": question_set_id,
        "cra4a_email": email,
        "cra4a_link": link,
        "cra4a_status": "assigned"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json"
    }

    response = requests.post(url, json=data, headers=headers)

    if not response.ok:
        print(f"[ERROR] Failed to send to Dataverse:")
        # print(f"[DEBUG] Payload: {data}")
        # print(f"[DEBUG] Response: {response.status_code} {response.text}")
    else:
        print(f"[OK] Synced to Dataverse: user {user_id}, set {question_set_id}")


def get_dataverse_access_token():
    token_url = f"https://login.microsoftonline.com/{settings.tenant_id}/oauth2/v2.0/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "scope": f"{settings.dataverse_api_url}/.default"
    }

    # print(f"[DEBUG] Token URL: {token_url}")
    # print(f"[DEBUG] Client ID: {settings.client_id}")
    # print(f"[DEBUG] Scope: {settings.dataverse_api_url}/.default")

    res = requests.post(token_url, data=data)

    if not res.ok:
        print(f"[ERROR] Token request failed: {res.status_code}")
        print(f"[ERROR] Response: {res.text}")

    res.raise_for_status()
    return res.json()["access_token"]