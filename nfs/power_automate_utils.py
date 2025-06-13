import requests
import time

def verificar_status_fluxo(run_id, flow_id, environment_id, access_token):
    """
    Verifica repetidamente o status de execução de um fluxo até que ele seja concluído.
    """
    url = f"https://management.azure.com/providers/Microsoft.ProcessSimple/environments/{environment_id}/flows/{flow_id}/runs/{run_id}?api-version=2016-11-01"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Erro ao consultar status do fluxo ({response.status_code})")
            print(response.text)
            break

        data = response.json()
        status = data["properties"]["status"]

        print(f"🔄 Status da execução {run_id}: {status}")

        if status == "Succeeded":
            print("✅ Execução concluída com sucesso!")
            return True
        elif status == "Failed":
            raise Exception("❌ Execução do fluxo falhou!")
        else:
            time.sleep(5)
