from werkzeug.security import generate_password_hash

password = "password here"  # Укажите новый пароль
hashed_password = generate_password_hash(password, method='scrypt')
print(hashed_password)

#INSERT INTO users (username, password, is_admin)
#VALUES ('new_admin', 'hashed_password_here', 1);
