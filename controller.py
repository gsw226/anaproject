from passlib.hash import pbkdf2_sha256

# 암호화
def hash_password(original_password):
    salt = 'gsw226'
    password = original_password + salt
    hashed_password = pbkdf2_sha256.hash(password)
    return hashed_password

# 복호화
def unhash_password(original_password, hashed_password):
    salt = 'gsw226'
    password = original_password + salt
    return pbkdf2_sha256.verify(password, hashed_password)