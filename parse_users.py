import json
import mysql.connector

# Step 1: Load the JSON file
with open('users.json', 'r') as file:
    data = json.load(file)

# Step 2: Connect to MySQL
db = mysql.connector.connect(
    host="localhost",  # Change this to your MySQL host
    user="root",  # Change this to your MySQL username
    password="bobby",  # Change this to your MySQL password
    database="TartanHacks2025"  # Change this to your MySQL database name
)

cursor = db.cursor()

# Step 3: Iterate through the JSON data and insert into MySQL
for username, user_data in data.items():
    if isinstance(user_data, dict) and "carbon_history" in user_data:
        for entry in user_data["carbon_history"]:
            timestamp = entry["timestamp"]
            carbon_score = entry["carbon_score"]
            offset_cost = entry["offset_cost"]

            # Step 4: Insert the data into MySQL
            sql = "INSERT INTO carbon_scores (username, timestamp, carbon_score, offset_cost) VALUES (%s, %s, %s, %s)"
            values = (username, timestamp, carbon_score, offset_cost)
            cursor.execute(sql, values)

# Step 5: Commit the transaction
db.commit()

# Step 6: Close the connection
cursor.close()
db.close()
