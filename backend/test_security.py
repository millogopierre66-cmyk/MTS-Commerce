import requests


BASE_URL = "http://127.0.0.1:8000"


def print_result(test_name, response):
    print("-" * 60)
    print(test_name)
    print("Status :", response.status_code)

    try:
        print("Response :", response.json())
    except Exception:
        print("Response :", response.text)


# ==========================================================
# TEST 1 : ACCÈS SANS AUTHENTIFICATION
# ==========================================================

response = requests.get(
    f"{BASE_URL}/accounting/dashboard"
)

print_result(
    "TEST 1 - Accès sans token",
    response
)


# ==========================================================
# TEST 2 : TOKEN INVALIDE
# ==========================================================

headers = {
    "Authorization": "Bearer token_invalide"
}

response = requests.get(
    f"{BASE_URL}/accounting/dashboard",
    headers=headers
)

print_result(
    "TEST 2 - Token invalide",
    response
)


# ==========================================================
# TEST 3 : CONNEXION ADMIN
# ==========================================================

login_data = {
    "username": "admin",
    "password": "Admin123!"
}

response = requests.post(
    f"{BASE_URL}/auth/login",
    data=login_data
)

print_result(
    "TEST 3 - Connexion administrateur",
    response
)


if response.status_code != 200:
    print("\nImpossible de continuer : connexion admin échouée.")
    exit()


token = response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}"
}


# ==========================================================
# TEST 4 : ADMIN → COMPTABILITÉ
# ==========================================================

response = requests.get(
    f"{BASE_URL}/accounting/dashboard",
    headers=headers
)

print_result(
    "TEST 4 - Admin accès comptabilité",
    response
)