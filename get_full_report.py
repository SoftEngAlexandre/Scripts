import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
from datetime import datetime
import time

print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')

# Diretório do arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
# Diretório para salvar o CSV
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\SAVE_EXPORTS'

# Carregar credenciais
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

# Autenticação base64
authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')

# Obter token
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.post(auth_url, data=request_body, headers=request_headers)
if response.status_code == 200:
    print('TOKEN obtido com sucesso!')
else:
    print(f'Falha ao obter TOKEN: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

response_json = response.json()
requestHeaders = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}"
}

# ---------------------------------------------------------- #
# ------------------- CONFIGURAÇÕES API -------------------- #
# ---------------------------------------------------------- #

api_url = f'https://api.{ENVIRONMENT}'
api_get = f'{api_url}/api/v2/users'
api_get_location = f'{api_url}/api/v2/locations'
api_get_roles_divisions = f'{api_url}/api/v2/authorization/subjects'
api_get_queues = f'{api_url}/api/v2/users'
api_get_groups = f'{api_url}/api/v2/groups'
pageNumber = 1
pageSize = 100
sortOrder = 'ascending'
expand = 'skills%2Clocations%2Cteam%2Cgroups'
all_users = []
all_locations = []
all_groups = []
dataAtual = datetime.now().strftime('%Y%m%d')
filename = 'Users'

# ---------------------------------------------------------- #
# ---------------------- FUNÇÕES BASE ---------------------- #
# ---------------------------------------------------------- #

def jsonReturn(pageSize):
    url_get = f'{api_get}?pageNumber={pageNumber}&pageSize={pageSize}&sortOrder={sortOrder}&expand={expand}'
    response = requests.get(url_get, headers=requestHeaders)
    data = response.json()
    with open('ExportJSON.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print('JSON gerado com sucesso')

def write_header():
    headers = [
        'ID', 'Nome', 'Email', 'Phone', 'Título', 'Departamento',
        'Gerente', 'Email do Gerente', 'Locação', 'Roles', 'Filas',
        'Divisão', 'Equipe', 'Skills', 'Grupos', 'Auto Answer'
    ]
    with open(f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
    print('Cabeçalho CSV criado com sucesso!')

def get_all_users(pageNumber):
    url_get = f'{api_get}?pageNumber={pageNumber}&pageSize={pageSize}&sortOrder={sortOrder}&expand={expand}'
    response = requests.get(url_get, headers=requestHeaders)
    if response.status_code == 200:
        data = response.json()
        number_of_pages = data["pageCount"]
    for user in data['entities']:
        all_users.append(user)
    print('Usuários da página', pageNumber, 'adicionados com sucesso.')
    if number_of_pages > pageNumber:
        next_page = pageNumber + 1
        get_all_users(next_page)

def get_all_locations():
    response = requests.get(api_get_location, headers=requestHeaders)
    if response.status_code == 200:
        data = response.json()
        for location in data['entities']:
            all_locations.append(location)

def get_all_groups():
    response = requests.get(f'{api_get_groups}?pageSize=100', headers=requestHeaders)
    if response.status_code == 200:
        data = response.json()
        for group in data['entities']:
            all_groups.append(group)

def get_user_email(id_manager):
    for user in all_users:
        if user['id'] == id_manager:
            return user['email']

def get_user_name(id_manager):
    for user in all_users:
        if user['id'] == id_manager:
            return user['name']

def get_location(location_id):
    for location in all_locations:
        if location_id == location['id']:
            return location['name']

def get_group(groups_id):
    ids = []
    names = []
    for group in groups_id:
        ids.append(group['id'])
    for id in ids:
        for group in all_groups:
            if id == group['id']:
                names.append(group['name'])
    return ', '.join(names)

def get_roles_and_divisions(id_user):
    url_get = f'{api_get_roles_divisions}/{id_user}'
    response = requests.get(url_get, headers=requestHeaders)
    if response.status_code == 200:
        data = response.json()
        roles_divisions = []
        for role in data['grants']:
            division_name = 'All Divisions' if role['division']['id'] == '*' else role['division']['name']
            role_name = role['role']['name']
            roles_divisions.append(f"{role_name}:[{division_name}]")
        return ', '.join(roles_divisions)
    else:
        print(f"Erro ao obter roles/divisions para o usuário {id_user}: {response.status_code} - {response.reason}")
        return ''

def get_queues(id_user, retries=5):
    url_get = f'{api_get_queues}/{id_user}/queues?pageSize={pageSize}'
    for attempt in range(retries):
        response = requests.get(url_get, headers=requestHeaders)
        if response.status_code == 200:
            data = response.json()
            queues = [queue['name'] for queue in data.get('entities', [])]
            return ', '.join(queues)
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"Erro 429 - Too Many Requests. Tentativa {attempt+1}/{retries}. Aguardando {retry_after}s...")
            time.sleep(retry_after)
        else:
            print(f"Erro ao obter filas para o usuário {id_user}: {response.status_code} - {response.reason}")
            return ''
    print(f"Falha ao obter filas para o usuário {id_user} após {retries} tentativas.")
    return ''

def get_skills(skills):
    all_skills = []
    for skill in skills:
        skill_name = skill['name']
        proficiency = skill['proficiency']
        skill_proficiency = f"{skill_name}:{int(proficiency)}"
        all_skills.append(skill_proficiency)
    return ', '.join(all_skills) if all_skills else ''

def get_addresses(addresses, email, phone):
    for adress in addresses:
        mediaType = adress['mediaType']
        if mediaType == 'EMAIL':
            email = adress['address']
        if mediaType in ('PHONE', 'SMS'):
            phone = adress['display']
    return email, phone

# ---------------------------------------------------------- #
# ------------- EXPORTAÇÃO EM BLOCOS DE 20 ----------------- #
# ---------------------------------------------------------- #

def write_csv_data_in_batches(batch_size=20, delay=5):
    total_users = len(all_users)
    print(f'Iniciando exportação de {total_users} usuários em blocos de {batch_size}...')

    with open(f'{output_directory}/{CUSTOMER}_{filename}_{dataAtual}.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for i in range(0, total_users, batch_size):
            batch = all_users[i:i + batch_size]
            print(f'Processando bloco {i // batch_size + 1} de {((total_users - 1) // batch_size) + 1}...')

            for user in batch:
                get_id = user['id']
                get_name = user['name']
                email, phone = get_addresses(user['addresses'], email='', phone='')
                email = user['email']
                get_title = user.get('title', '')
                get_department = user.get('department', '')
                get_manager_id = user['manager'].get('id') if 'manager' in user else None
                get_name_manager = get_user_name(get_manager_id)
                get_email_manager = get_user_email(get_manager_id)
                get_location_id = user['locations'][0]['locationDefinition']['id'] if user['locations'] else ''
                get_location_work = get_location(get_location_id)
                get_role_division = get_roles_and_divisions(get_id)
                get_queue = get_queues(get_id)
                get_division = user['division'].get('name')
                get_team = user['team'].get('name', '') if 'team' in user else ''
                get_skill = get_skills(user['skills'])
                get_groups = get_group(user['groups'])
                get_auto_answer = user.get('acdAutoAnswer', '')

                writer.writerow([
                    get_id,
                    get_name,
                    email,
                    phone,
                    get_title,
                    get_department,
                    get_name_manager,
                    get_email_manager,
                    get_location_work,
                    get_role_division,
                    get_queue,
                    get_division,
                    get_team,
                    get_skill,
                    get_groups,
                    get_auto_answer
                ])

            print(f'Bloco {i // batch_size + 1} concluído. Aguardando {delay} segundos...')
            time.sleep(delay)

    print(f'\nExportação concluída! Arquivo salvo em: {output_directory}')

# ---------------------------------------------------------- #
# ---------------------- EXECUÇÃO FINAL -------------------- #
# ---------------------------------------------------------- #

get_all_users(pageNumber)
get_all_locations()
get_all_groups()
write_header()
write_csv_data_in_batches(batch_size=20, delay=5)

print('---------------------------------')
print('Processo finalizado com sucesso!')
print(f'Arquivo CSV salvo em: {output_directory}')
print('---------------------------------')
