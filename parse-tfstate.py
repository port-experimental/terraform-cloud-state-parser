import os
import requests
import json

TFC_TOKEN = os.getenv("TFC_TOKEN")
TFC_ORG = os.getenv("TFC_ORG")
PORT_WEBHOOK_URL = os.getenv("PORT_WEBHOOK_URL")

if not TFC_TOKEN or not TFC_ORG:
    raise EnvironmentError("Please set TFC_TOKEN and TFC_ORG environment variables.")

API_URL = "https://app.terraform.io/api/v2"
HEADERS = {
    "Authorization": f"Bearer {TFC_TOKEN}",
    "Content-Type": "application/vnd.api+json"
}

def list_workspaces(org):
    url = f"{API_URL}/organizations/{org}/workspaces"
    workspaces = []
    while url:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        workspaces.extend(data.get("data", []))
        url = data.get("links", {}).get("next")
    return workspaces

def get_current_state_version(workspace_id):
    url = f"{API_URL}/workspaces/{workspace_id}/current-state-version"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 404:
        # No state version found for this workspace
        return None
    resp.raise_for_status()
    return resp.json()

def download_state_file(download_url):
    resp = requests.get(download_url, headers=HEADERS)
    resp.raise_for_status()
    return resp.text

def send_port_webhook(payload):
    """
    Send a POST request to a Port webhook URL supplied via the PORT_WEBHOOK_URL environment variable.
    """
    if not PORT_WEBHOOK_URL:
        raise EnvironmentError("Please set PORT_WEBHOOK_URL environment variable.")
    headers = {"Content-Type": "application/json"}
    resp = requests.post(PORT_WEBHOOK_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json() if resp.content else None

if __name__ == "__main__":
    workspaces = list_workspaces(TFC_ORG)
    for ws in workspaces:
        ws_id = ws["id"]
        ws_name = ws["attributes"]["name"]
        print(f"Processing workspace: {ws_name} ({ws_id})")
        state_info = get_current_state_version(ws_id)
        if not state_info:
            print(f"No state version found for workspace: {ws_name}")
            continue
        download_url = state_info.get("data", {}).get("attributes", {}).get("hosted-state-download-url")
        if download_url:
            state = download_state_file(download_url)
            try:
                state_json = json.loads(state)           
                if isinstance(state_json, list):
                    state_list = state_json
                else:
                    state_list = [state_json]
            except json.JSONDecodeError:
                print(f"Failed to parse state file for workspace: {ws_name}")
                state_list = []
                print(state_list)
            for item in state_list:
                resources = item.get("resources", [])
                for res in resources:
                    res["workspace_id"] = ws_id
                    print(f"Sending resource {res.get('name')} to Port via webhook")
                    try:
                        response = send_port_webhook(res)
                        print(f"Successfully sent resource {res.get('name')} to Port. Response: {response}")
                    except Exception as e:
                        print(f"Failed to send resource {res.get('name')} to Port. Error: {e}")
        else:
            print(f"No state file found for workspace: {ws_name}")