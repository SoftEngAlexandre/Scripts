import os
import requests
import pandas as pd
from dotenv import load_dotenv


load_dotenv(dotenv_path=r"C:\Users\alexandre.ferreira\Desktop\Code\ENV\.env")

CLIENT_ID = os.getenv("GENESYS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GENESYS_CLIENT_SECRET")


ENVIRONMENT = (
    os.getenv("GENESYS_ENVIRONMENT")
    or os.getenv("ENVIRONMENT")
    or "sae1.pure.cloud"
)


def get_token():
    url = f"https://login.{ENVIRONMENT}/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(url, data=data, headers=headers)
    if r.status_code != 200:
        print(f" Erro ao obter token: {r.status_code} - {r.text}")
        r.raise_for_status()

    token = r.json().get("access_token")
    print("✅ Token obtido com sucesso")
    return token


def delete_skill_from_user(user_id, skill_id, token):
    url = f"https://api.{ENVIRONMENT}/api/v2/users/{user_id}/routingskills/{skill_id}"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.delete(url, headers=headers)
    if r.status_code == 204:
        print(f" Skill {skill_id} removida do usuário {user_id}")
    elif r.status_code == 404:
        print(f" Usuário ou skill não encontrados: user={user_id}, skill={skill_id}")
    else:
        print(f" Erro ao remover skill {skill_id} de {user_id}: {r.status_code} - {r.text}")


def main():
    
    users_csv = r"C:\Users\alexandre.ferreira\Desktop\Code\five_stars_users.csv"
    skills_csv = r"C:\Users\alexandre.ferreira\Desktop\Code\five_stars_skill.csv"

   
    df_users = pd.read_csv(users_csv)
    df_skills = pd.read_csv(skills_csv)

    if "userId" not in df_users.columns:
        raise ValueError ("O arquivo users.csv deve conter a coluna 'userId'")
    if "skillId" not in df_skills.columns:
        raise ValueError("O arquivo skills.csv deve conter a coluna 'skillId'")

  
    token = get_token()


    for _, user_row in df_users.iterrows():
        user_id = str(user_row["userId"]).strip()
        for _, skill_row in df_skills.iterrows():
            skill_id = str(skill_row["skillId"]).strip()
            delete_skill_from_user(user_id, skill_id, token)

if __name__ == "__main__":
    main()
