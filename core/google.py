from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


def verify_google_id_token(token: str) -> dict | None:
    try:
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        return {
            "email": info["email"],
            "full_name": info.get("name", ""),
            "google_id": info["sub"],
        }

    except Exception:
        return None
