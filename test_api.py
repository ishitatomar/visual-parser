import requests

url = "http://127.0.0.1:5000/api/parse"
data = {
    "grammar": "E -> T E'\nE' -> + T E' | epsilon\nT -> F T'\nT' -> * F T' | epsilon\nF -> ( E ) | id",
    "input": "id + id * id"
}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        res_json = response.json()
        print("Keys in response:", list(res_json.keys()))
        if "error" in res_json:
            print("API Error:", res_json["error"])
        else:
            print("Successfully received sets, tokens, LL1, LR1, and LALR data.")
            print("LL1 Conflicts:", res_json.get("ll1", {}).get("conflicts"))
            print("LALR Conflicts:", res_json.get("lalr", {}).get("conflicts"))
    else:
        print("Failed:", response.text)
except requests.exceptions.ConnectionError:
    print("Server not running.")
