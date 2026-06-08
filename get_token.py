"""
Запустіть ОДИН РАЗ на своєму комп'ютері, щоб отримати токен.
Потрібен файл client_secret.json (OAuth Desktop app) у цій же папці.

  pip install google-auth-oauthlib
  python get_token.py

Відкриється браузер — увійдіть у Google-акаунт каналу
"Українська Церква у Швейцарії". Скрипт виведе JSON —
скопіюйте його ПОВНІСТЮ у секрет GitHub з ім'ям YT_TOKEN.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    ["https://www.googleapis.com/auth/youtube"],
)
creds = flow.run_local_server(port=0)
print("\n=== СКОПІЮЙТЕ ВСЕ НИЖЧЕ У СЕКРЕТ YT_TOKEN ===\n")
print(creds.to_json())
