import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
import datetime
import logging
from time import sleep

# -------------------- LOGS --------------------
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\Python_v2\logs\{data_atual}_Audit.log"
os.makedirs(os.path.dirname(nome_arquivo_log), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print("--------------- Iniciando Script ---------------")

# -------------------- ENV --------------------
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\LOCALLOCAL\EXPORT'
load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {'Authorization': f'Basic {authorization}', 'Content-Type': 'application/x-www-form-urlencoded'}

proxies = {'http': 'http://10.104.244.30:8080', 'https': 'http://10.104.244.30:8080'}
proxy = 'n'

# -------------------- TOKEN --------------------
if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)

if response.status_code == 200:
    logging.info("TOKEN gerado com sucesso")
else:
    logging.error(f'Falha ao gerar token: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

response_json = response.json()
requestHeaders = {'Authorization': f"{response_json['token_type']} {response_json['access_token']}"}

import base64
import requests
import sys
import os
import csv
from dotenv import load_dotenv
import json
import datetime
import logging
from time import sleep

# -------------------- LOGS --------------------
data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
nome_arquivo_log = fr"C:\Users\alexandre.ferreira\Desktop\Python_v2\logs\{data_atual}_Audit.log"
os.makedirs(os.path.dirname(nome_arquivo_log), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=nome_arquivo_log, format="%(asctime)s - %(levelname)s - %(message)s")
print("--------------- Iniciando Script ---------------")

# -------------------- ENV --------------------
env_file = r'C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env'
output_directory = r'C:\Users\alexandre.ferreira\Desktop\Code\LOCALLOCAL\EXPORT'
load_dotenv(env_file)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
CUSTOMER = os.getenv('CUSTOMER')

authorization = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'ISO-8859-1')).decode('ascii')
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {'Authorization': f'Basic {authorization}', 'Content-Type': 'application/x-www-form-urlencoded'}

proxies = {'http': 'http://10.104.244.30:8080', 'https': 'http://10.104.244.30:8080'}
proxy = 'n'

# -------------------- TOKEN --------------------
if proxy == 's':
    response = requests.post(auth_url, data=request_body, headers=request_headers, proxies=proxies)
else:
    response = requests.post(auth_url, data=request_body, headers=request_headers)

if response.status_code == 200:
    logging.info("TOKEN gerado com sucesso")
else:
    logging.error(f'Falha ao gerar token: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)

response_json = response.json()
requestHeaders = {'Authorization': f"{response_json['token_type']} {response_json['access_token']}"}

# -------------------- PARÂMETROS --------------------
api_url = f'https://api.{ENVIRONMENT}'
api_audit_query = f'{api_url}/api/v2/audits/query/'
pageSize = 100
mode = input('Digite o modo de execução (full/basic): ')
filename = 'Audit'

# -------------------- FUNÇÕES --------------------
def post_audit_query(body):
    if proxy == 's':
        r = requests.post(api_audit_query, json=body, headers=requestHeaders, proxies=proxies)
    else:
        r = requests.post(api_audit_query, json=body, headers=requestHeaders)
    return r

def verificaPost(post_response):
    if post_response.status_code in [200, 202]:
        transaction_id = post_response.json()['id']
        print('Transaction ID:', transaction_id)
        return transaction_id
    else:
        logging.error(f'Falha no POST: {post_response.status_code} - {post_response.reason}')
        logging.error(post_response.text)
        sys.exit(post_response.status_code)

def tempo(wait):
    sleep(wait)

def consultaStatus(transaction_id):
    url_get_status = f'{api_audit_query}{transaction_id}'
    if proxy == 's':
        response = requests.get(url_get_status, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.get(url_get_status, headers=requestHeaders)
    status = response.json().get('state','')
    print('Status da Query:', status)
    if status == 'Running':
        print('Aguardando 10 segundos...')
        tempo(10)
        consultaStatus(transaction_id)

def get_result_query(transaction_id):
    url_results = f'{api_audit_query}{transaction_id}/results?pageSize={pageSize}'
    if proxy == 's':
        response = requests.get(url_results, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.get(url_results, headers=requestHeaders)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Falha ao obter resultados: {response.status_code} - {response.reason}')
        sys.exit(response.status_code)

def jsonReturn(transaction_id):
    data = get_result_query(transaction_id)
    with open('ExportJSON.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('JSON gerado com sucesso')

def write_header(mode):
    colunas_full = ['service_name','level','action_id','action_type','action_status','event_date','entity_type',
                    'entity_id','entity_name','usuario_executor','usuario_executado','old_values','new_values',
                    'change_property','remote_ip','application','client','context','entityChanges','message','propertyChanges']
    colunas_basic = ['level','action_type','action_status','event_date','entity_type','entity_name','usuario_executor',
                     'usuario_executado','old_values','new_values','remote_ip']
    with open(f'{output_directory}/{CUSTOMER}_{filename}_{data_atual}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(colunas_full if mode=='full' else colunas_basic)
    print('Cabeçalho CSV escrito com sucesso!')

def get_usuario_executado(service_name, action):
    if service_name == 'Presence':
        return action.get('entity', {}).get('id', '')
    if 'propertyChanges' in action:
        props = [p.get('property','') for p in action.get('propertyChanges',[])]
        return ', '.join([p[49:85] for p in props if len(p)>=85])
    return ''

def get_user(id_usuario):
    if not id_usuario:
        return ''
    url = f'{api_url}/api/v2/users/{id_usuario}'
    if proxy=='s':
        response = requests.get(url, headers=requestHeaders, proxies=proxies)
    else:
        response = requests.get(url, headers=requestHeaders)
    if response.status_code == 200:
        return response.json().get('name','')
    else:
        logging.error(f'Falha ao buscar usuário {id_usuario}: {response.status_code} - {response.reason}')
        return id_usuario

def write_data(transaction_id, mode):
    data = get_result_query(transaction_id)
    output_file = f'{output_directory}/{CUSTOMER}_{filename}_{data_atual}.csv'

    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for action in data.get('entities', []):
            service_name = action.get('serviceName', '')
            level = action.get('level', '')
            action_id = action.get('id', '')
            action_type = action.get('action', '')
            action_status = action.get('status', '')
            event_date = action.get('eventDate', '')
            entity_type = action.get('entityType', '')
            entity_id = action.get('entity', {}).get('id', '')
            entity_name = action.get('entity', {}).get('name', '')
            usuario_executor = get_user(action.get('user', {}).get('id')) if service_name=='ContactCenter' else action.get('user', {}).get('id','')
            usuario_executado = get_user(get_usuario_executado(service_name, action)) if service_name=='ContactCenter' else get_usuario_executado(service_name, action)

            propertyChanges = action.get('propertyChanges', [])
            old_values = ', '.join([v for p in propertyChanges for v in p.get('oldValues',[])])
            new_values = ', '.join([v for p in propertyChanges for v in p.get('newValues',[])])
            property_change = ', '.join([p.get('property','') for p in propertyChanges])

            remote_ip = ', '.join(action.get('remoteIp', [])) if isinstance(action.get('remoteIp'), list) else ''
            context = json.dumps(action.get('context',''), ensure_ascii=False)
            entityChanges = json.dumps(action.get('entityChanges',''), ensure_ascii=False)
            message = action.get('message','')
            application = action.get('application','')
            client = action.get('client','')

            if mode=='full':
                writer.writerow([service_name,level,action_id,action_type,action_status,event_date,entity_type,entity_id,
                                 entity_name,usuario_executor,usuario_executado,old_values,new_values,property_change,
                                 remote_ip,application,client,context,entityChanges,message,propertyChanges])
            else:
                writer.writerow([level,action_type,action_status,event_date,entity_type,entity_name,usuario_executor,
                                 usuario_executado,old_values,new_values,remote_ip])
            print(f'Ação {action_id} escrita com sucesso.')

# -------------------- EXECUÇÃO --------------------
body = {
    "interval": "2025-02-21T11:30:00Z/2025-02-22T23:00:00Z",
    "serviceName": "Presence",  # trocar para Presence para monitorar status de agentes
    "filters": [{"property":"UserId","value":"12124e20-0819-4698-877f-a201fc12eee1"}]
}

post_response = post_audit_query(body)
transaction_id = verificaPost(post_response)
print('Aguardando 10 segundos para consulta de status...')
tempo(10)
consultaStatus(transaction_id)
jsonReturn(transaction_id)  # opcional
write_header(mode)
write_data(transaction_id, mode)
print(f'Arquivo salvo em {output_directory}')