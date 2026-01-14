import requests
import json
import yaml
import time
from time import sleep

URL_BASE = "https://app.omie.com.br/api/v1/"

def extrair_lista(resp_json):
    """
    A Omie não padroniza o nome da lista.
    Essa função encontra automaticamente a lista de dados.
    """
    for key, value in resp_json.items():
        if isinstance(value, list):
            return key, value
    return None, []

start_time = time.time()

# ---- LÊ CONFIGURAÇÕES ----
with open("keys.yaml", "r") as f:
    keys = yaml.safe_load(f)

with open("routes.yaml", "r") as f:
    routes = yaml.safe_load(f)

# ---- LOOP PRINCIPAL ----
for app_key, app_secret in keys["keys"]:

    print(f"\n🔑 Usando APP_KEY: {app_key}")

    for route, call in routes["routes"]:

        print(f"\n➡️ Extraindo: {call}")

        filename = f"{call}.json"

        params = {
            "call": call,
            "app_key": app_key,
            "app_secret": app_secret,
            "param": [
                {
                    "pagina": 1,
                    "registros_por_pagina": 100,
                    "apenas_importado_api": "N"
                }
            ]
        }

        data = []
        page = 1

        while True:
            params["param"][0]["pagina"] = page

            url = f"{URL_BASE}{route}"

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                url,
                headers=headers,
                json=params  # 👈 JSON VAI NO BODY
            )

            if response.status_code != 200:
                print(f"❌ Erro HTTP {response.status_code}")
                break

            resp_json = response.json()
            lista_nome, lista = extrair_lista(resp_json)

            if not lista:
                print("✅ Fim da paginação")
                break

            print(f"📄 Página {page} → {len(lista)} registros ({lista_nome})")

            data.extend(lista)
            page += 1
            sleep(1)  # evita bloqueio da Omie

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Salvo: {filename} ({len(data)} registros)")

print(f"\n⏱️ Tempo total: {round((time.time() - start_time)/60, 2)} minutos")
