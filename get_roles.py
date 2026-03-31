import base64
import requests
import sys
import os
from dotenv import load_dotenv
import datetime
import logging
import re
import pandas as pd
from pathlib import Path

# ==============================
# CONFIG INICIAL
# ==============================

data_atual = datetime.datetime.now().strftime("%Y-%m-%d")

log_path = Path(r"C:\Users\alexandre.ferreira\Desktop\Python_v2\logs") / f"{data_atual}_Queues.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=log_path,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

print('--- Iniciando Script ---')

# ==============================
# ENV
# ==============================

env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
output_directory = Path(r'C:\Users\alexandre.ferreira\Desktop\Code\zzzz')

load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

if not all([CLIENT_ID, CLIENT_SECRET, ENVIRONMENT]):
    logging.error("Variáveis de ambiente faltando")
    sys.exit(1)

# ==============================
# AUTH
# ==============================

auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

auth_url = f'https://login.{ENVIRONMENT}/oauth/token'

headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

body = {'grant_type': 'client_credentials'}

response = requests.post(auth_url, data=body, headers=headers)

if response.status_code != 200:
    logging.error(f'Erro ao gerar token: {response.status_code} - {response.text}')
    sys.exit(1)

token_data = response.json()
access_token = token_data['access_token']

print('TOKEN OK')

# ==============================
# API ROLES
# ==============================

api_url = f'https://api.{ENVIRONMENT}/api/v2/authorization/roles'

headers = {
    'Authorization': f'Bearer {access_token}'
}

roles_permissions = {}

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

page = 1
page_size = 100

while True:
    url = f"{api_url}?pageNumber={page}&pageSize={page_size}&sortOrder=ascending"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f'Erro API: {response.status_code} - {response.text}')
        sys.exit(1)

    data = response.json()

    for role in data.get('entities', []):
        role_name = sanitize_filename(role['name'])

        permissions = []
        for policy in role.get('permissionPolicies', []):
            domain = policy['domain']
            entity = policy['entityName']
            actions = ', '.join(policy['actionSet'])

            permissions.append(f"{domain}.{entity}: {actions}")

        roles_permissions[role_name] = permissions

        print(f'✔ {role_name}')

    if page >= data.get('pageCount', 1):
        break

    page += 1

# ==============================
# EXPORT
# ==============================

df = pd.DataFrame({k: pd.Series(v) for k, v in roles_permissions.items()})

output_directory.mkdir(parents=True, exist_ok=True)

excel_path = output_directory / f"{data_atual}_{CUSTOMER}_Roles_Permissions.xlsx"

df.to_excel(excel_path, index=False)

print(f'\nArquivo gerado: {excel_path}')