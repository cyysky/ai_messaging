import sqlite3

# Connect to the database
conn = sqlite3.connect('../backend/backend.db')
cursor = conn.cursor()

# Update the phone number for user "Chong Yoe Yat" (using username)
cursor.execute(
    "UPDATE users SET phone_number = ? WHERE username = ?",
    ("+60127939038", "Chong Yoe Yat")
)

# Commit the changes
conn.commit()

# Verify the update
cursor.execute(
    "SELECT id, username, full_name, phone_number FROM users WHERE username = ?",
    ("Chong Yoe Yat",)
)
result = cursor.fetchone()
if result:
    print(f"User updated successfully:")
    print(f"  ID: {result[0]}")
    print(f"  Username: {result[1]}")
    print(f"  Full Name: {result[2]}")
    print(f"  Phone Number: {result[3]}")
else:
    print("User not found!")

conn.close()