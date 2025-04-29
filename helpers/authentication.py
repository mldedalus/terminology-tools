# Fetch an access token
def fetch_token(token_url, client_id, client_secret):
    import requests
    print(f"Calling {token_url} for clientid {client_id}")
    data = {
        "grant_type"    : "client_credentials",
        "client_id"     : client_id,
        "client_secret" : client_secret,
    }
    request = requests.post(f'{token_url}', data=data)

    if request.status_code == 200:
        response = request.json()
        token = response.get('access_token')
        return token
    else:
        raise Exception(f"Failed to retrieve token with status code {request.status_code}: {request.text}.")
