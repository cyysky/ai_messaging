import sqlite3

# Connect to the database
conn = sqlite3.connect('backend/backend.db')
cursor = conn.cursor()

# List all users
cursor.execute("SELECT id, username, full_name, phone_number FROM users")
results = cursor.fetchall()

print("Users in database:")
for row in results:
    print(f"  ID: {row[0]}, Username: {row[1]}, Full Name: {row[2]}, Phone: {row[3]}")

conn.close()