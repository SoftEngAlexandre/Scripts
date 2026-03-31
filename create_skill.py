import os
import csv
import time
import requests
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ENVIRONMENT = os.getenv("ENVIRONMENT", "sae1.pure.cloud")

CSV_FILE = r"C:\Users\alexandre.ferreira\Desktop\Code\TRIGG\skills.csv"
LOG_FILE = r"C:\Users\alexandre.ferreira\Desktop\Code\TRIGG\create_skills.log"
BATCH_SIZE = 50
DELAY_BETWEEN_BATCHES = 3  # segundos


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger().addHandler(logging.StreamHandler())


def get_token():
    url = f"https://login.{ENVIRONMENT}/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200:
            token = response.json().get("access_token")
            logging.info("Token obtido com sucesso.")
            return token
        else:
            logging.error(f"Erro ao autenticar: {response.status_code} - {response.text}")
            raise Exception("Falha na autenticação.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de conexão ao obter token: {e}")
        raise


def read_skills_from_csv(csv_file):
    skills = []
    with open(csv_file, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row.get("name")
            if name:
                skills.append(name.strip())
    logging.info(f"{len(skills)} skills lidas do arquivo CSV.")
    return skills


def create_skill(session, token, skill_name):
    url = f"https://api.{ENVIRONMENT}/api/v2/routing/skills"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"name": skill_name}
    response = session.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        logging.info(f"Skill criada: {skill_name}")
        return True
    elif response.status_code == 400:
        logging.warning(f"Skill já existe: {skill_name}")
        return True
    else:
        logging.error(f"Erro ao criar skill '{skill_name}': {response.status_code} - {response.text}")
        return False


def process_in_batches(skills, token):
    total = len(skills)
    session = requests.Session()
    for i in range(0, total, BATCH_SIZE):
        batch = skills[i:i + BATCH_SIZE]
        logging.info(f"Criando bloco {i // BATCH_SIZE + 1} de {((total - 1) // BATCH_SIZE) + 1}...")
        for skill_name in batch:
            create_skill(session, token, skill_name)
        if i + BATCH_SIZE < total:
            logging.info(f"Aguardando {DELAY_BETWEEN_BATCHES}s antes do próximo bloco...")
            time.sleep(DELAY_BETWEEN_BATCHES)

# =========================
# EXECUÇÃO PRINCIPAL
# =========================
def main():
    try:
        token = get_token()
        skills = read_skills_from_csv(CSV_FILE)
        if not skills:
            logging.warning("Nenhuma skill encontrada no CSV.")
            return
        process_in_batches(skills, token)
        logging.info("Processo concluído com sucesso.")
    except Exception as e:
        logging.error(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    main()
