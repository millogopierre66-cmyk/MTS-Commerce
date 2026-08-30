from app.security.hashing import hash_password, verify_password

password = "Admin123!"

hashed = hash_password(password)

print("Mot de passe :", password)
print("Hash :", hashed)
print("Vérification :", verify_password(password, hashed))