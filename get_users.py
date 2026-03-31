import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
from datetime import datetime

print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')

# Caminho para o arquivo .env e diretório de saída
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\LOCALLOCAL\EXPORT\users'

load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')

auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# ------------------- AUTENTICAÇÃO ------------------- #
response = requests.post(auth_url, data=request_body, headers=request_headers)
if response.status_code == 200:
    print('✅ TOKEN obtido com sucesso!')
else:
    print(f'❌ Falha ao obter token: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

response_json = response.json()
requestHeaders = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}"
}

# ------------------- ENDPOINTS ------------------- #
api_url = f'https://api.{ENVIRONMENT}'
api_get_users = f'{api_url}/api/v2/users'
api_get_roles = f'{api_url}/api/v2/users/{{userId}}/roles'

pageNumber = 1
pageSize = 100
sortOrder = 'ascending'
expand = 'skills%2Clocations%2Cteam%2Cgroups'
all_users = []
dataAtual = datetime.now().strftime('%Y%m%d')
filename = 'Users'

# ------------------- CSV HEADER ------------------- #
def write_header():
    headers = [
        'ID', 'Nome', 'PreferredName', 'Email', 'Título', 'Departamento',
        'Supervisor', 'Email do Supervisor', 'Auto Answer', 'Roles'
    ]
    os.makedirs(output_directory, exist_ok=True)
    with open(f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    print('✅ Cabeçalho CSV criado com sucesso!')

# ------------------- GET USERS PAGINADO ------------------- #
def get_all_users(pageNumber):
    url_get = f'{api_get_users}?pageNumber={pageNumber}&pageSize={pageSize}&sortOrder={sortOrder}&expand={expand}'
    response = requests.get(url_get, headers=requestHeaders)

    if response.status_code == 200:
        data = response.json()
        number_of_pages = data.get("pageCount", 1)
    else:
        print(f"❌ Erro ao buscar usuários: {response.status_code}")
        return

    all_users.extend(data.get('entities', []))
    print(f'📥 Usuários da página {pageNumber} adicionados com sucesso.')

    if number_of_pages > pageNumber:
        get_all_users(pageNumber + 1)

# ------------------- GET USER EMAIL/NOME ------------------- #
def get_user_email(id_manager):
    for user in all_users:
        if user['id'] == id_manager:
            return user.get('email', '')
    return ''

def get_user_name(id_manager):
    for user in all_users:
        if user['id'] == id_manager:
            return user.get('name', '')
    return ''

# ------------------- GET USER ROLES ------------------- #
def get_user_roles(user_id):
    response = requests.get(api_get_roles.format(userId=user_id), headers=requestHeaders)
    if response.status_code == 200:
        roles = response.json().get('entities', [])
        return ', '.join([role['name'] for role in roles])
    return ''

# ------------------- WRITE CSV ------------------- #
def write_csv_data():
    output_path = f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv'
    with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for user in all_users:
            get_id = user.get('id', '')
            get_name = user.get('name', '')
            get_preferred_name = user.get('preferredName', '')  # <- CAMPO ADICIONADO
            get_email = user.get('email', '')
            get_title = user.get('title', '')
            get_department = user.get('department', '')
            get_manager_id = user['manager'].get('id') if 'manager' in user and user['manager'] else ''
            get_name_manager = get_user_name(get_manager_id)
            get_email_manager = get_user_email(get_manager_id)
            get_auto_answer = user.get('acdAutoAnswer', '')
            get_roles = get_user_roles(get_id)

            writer.writerow([
                get_id,
                get_name,
                get_preferred_name,
                get_email,
                get_title,
                get_department,
                get_name_manager,
                get_email_manager,
                get_auto_answer,
                get_roles
            ])
            print(f"📝 Usuário {get_name} ({get_preferred_name}) exportado com sucesso.")

# ------------------- EXECUÇÃO ------------------- #
get_all_users(pageNumber)
write_header()
write_csv_data()
print(f'✅ Arquivo salvo em: {output_directory}')
