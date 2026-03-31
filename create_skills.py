import base64
import requests
import sys
import os
from dotenv import load_dotenv
 
print('---------------------------------')
print('- Genesys Cloud Python Client SDK')
print('---------------------------------')
 
# Definir o caminho absoluto para o arquivo .env
env_file = r'C:\Users\alexandre.ferreira\Desktop\ARQUIVOS\Python_v2\env_LOCAL\.env'
 
# Carregar as credenciais do arquivo .env
load_dotenv(env_file)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
 
# Verificar se as credenciais foram carregadas corretamente
if not all([CLIENT_ID, CLIENT_SECRET, ENVIRONMENT]):
    print("Erro: Verifique se as variáveis de ambiente (CLIENT_ID, CLIENT_SECRET, ENVIRONMENT) estão definidas corretamente.")
    sys.exit(1)
 
# Base64 encode the client ID and client secret
authorization = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode('ISO-8859-1')).decode('ascii')
 
# Prepare for POST /oauth/token request
auth_url = f'https://login.{ENVIRONMENT}/oauth/token'
request_body = {'grant_type': 'client_credentials'}
request_headers = {
    'Authorization': f'Basic {authorization}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
 
# Get token
response = requests.post(auth_url, data=request_body, headers=request_headers)
 
# Check response
if response.status_code == 200:
    print('TOKEN com SUCESSO!')
else:
    print(f'Falha na obtenção do token: {response.status_code} - {response.reason}')
    sys.exit(response.status_code)
 
# Get JSON response body
response_json = response.json()
 
# Prepare for GET /api/v2/authorization/roles request
request_headers = {
    'Authorization': f"{response_json['token_type']} {response_json['access_token']}"
}
 
# Define a função para realizar o POST
def post_skill_for_user(user_id, skill_data):
    api_url = f'https://api.{ENVIRONMENT}/api/v2/users/{user_id}/routingskills'
    post_skill_response = requests.post(api_url, json=skill_data, headers=request_headers)
    return post_skill_response
 
# Ler o arquivo ids.txt e realizar o POST para cada ID
with open('ids.txt', 'r') as file:
    for line in file:
        parts = line.strip().split(',')  
        if len(parts) != 3:
            print(f"Linha inválida no arquivo ids.txt: {line}")
            continue
       
        user_id = parts[0]  
        skill_id = parts[1]  
        proficiency = parts [2]
        body = {
            "id": skill_id,
            "proficiency": proficiency  #no caso é o numero de estrelas.
        }
       
        # Realizar o POST para o usuário
        post_response = post_skill_for_user(user_id, body)
       
        # Verificar a resposta para cada POST
        if post_response.status_code == 200:
            print(f'POST para usuário {user_id} com SUCESSO!')
        else:
            print(f'Falha no POST para usuário {user_id}: {post_response.status_code} - {post_response.reason}')
            print(post_response.json())
 
print("Todos os POSTs concluídos.")