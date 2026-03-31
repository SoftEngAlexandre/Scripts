import base64
import requests
import sys
import os
import csv
import time
from dotenv import load_dotenv
from datetime import datetime

print('---------------------------------')
print('- Genesys Cloud Routing Skills Export')
print('---------------------------------')

env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\LOCAL\EXPORT\routing_skills'

load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

authorization = base64.b64encode(
    bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')
).decode('ascii')

auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# ------------------- AUTENTICAÇÃO ------------------- #
response = requests.post(auth_url, data=request_body, headers=request_headers)

if response.status_code != 200:
    print(f'❌ Falha ao obter token: {response.status_code}')
    sys.exit(response.status_code)

print('✅ TOKEN obtido com sucesso!')

response_json = response.json()

requestHeaders = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}"
}

# ------------------- ENDPOINTS ------------------- #
api_url = f'https://api.{ENVIRONMENT}'
api_get_users = f'{api_url}/api/v2/users'
api_get_routing_skills = f'{api_url}/api/v2/users/{{userId}}/routingskills'

pageNumber = 1
pageSize = 100
all_users = []

dataAtual = datetime.now().strftime('%Y%m%d')
filename = 'RoutingSkills'

# ------------------- CSV HEADER ------------------- #
def write_header():
    headers = [
        'UserID',
        'Nome',
        'Email',
        'Skill ID',
        'Skill Name',
        'Proficiency'
    ]

    os.makedirs(output_directory, exist_ok=True)

    with open(f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv',
              'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

    print('✅ Cabeçalho CSV criado com sucesso!')

# ------------------- GET USERS PAGINADO ------------------- #
def get_all_users(pageNumber):
    url_get = f'{api_get_users}?pageNumber={pageNumber}&pageSize={pageSize}'
    response = requests.get(url_get, headers=requestHeaders)

    if response.status_code != 200:
        print(f"❌ Erro ao buscar usuários: {response.status_code}")
        return

    data = response.json()
    number_of_pages = data.get("pageCount", 1)

    all_users.extend(data.get('entities', []))
    print(f'📥 Página {pageNumber} adicionada.')

    if number_of_pages > pageNumber:
        get_all_users(pageNumber + 1)

# ------------------- GET ROUTING SKILLS ------------------- #
def get_user_routing_skills(user_id):
    response = requests.get(
        api_get_routing_skills.format(userId=user_id),
        headers=requestHeaders
    )

    if response.status_code == 200:
        return response.json().get('entities', [])
    else:
        print(f'⚠️ Erro ao buscar skills do usuário {user_id}')
        return []

# ------------------- WRITE CSV EM BLOCOS DE 5 ------------------- #
def write_csv_data():
    output_path = f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv'

    with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        total_users = len(all_users)
        block_size = 5

        for i in range(0, total_users, block_size):

            block = all_users[i:i + block_size]
            print(f'🚀 Processando usuários {i+1} até {i+len(block)}')

            for user in block:
                user_id = user.get('id', '')
                user_name = user.get('name', '')
                user_email = user.get('email', '')

                skills = get_user_routing_skills(user_id)

                if not skills:
                    writer.writerow([user_id, user_name, user_email, '', '', ''])
                    continue

                for skill in skills:
                    writer.writerow([
                        user_id,
                        user_name,
                        user_email,
                        skill.get('id', ''),
                        skill.get('name', ''),
                        skill.get('proficiency', '')
                    ])

                print(f'📝 Exportado: {user_name}')

            # Pequena pausa entre blocos
            time.sleep(1)

# ------------------- EXECUÇÃO ------------------- #
get_all_users(pageNumber)
write_header()
write_csv_data()

print(f'✅ Arquivo salvo em: {output_directory}')