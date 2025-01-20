import mysql.connector

def batch_inserts(file_path):
    # Establish connection to the MySQL database
    db = mysql.connector.connect(
        host="127.0.0.1",
        port=15306,
        user="user",
        password="",
        database="dbms"
    )
    cursor = db.cursor()

    try:
        with open(file_path, 'r') as file:
            # Read the first line to get the insert statement
            insert_statement = file.readline().strip()
            
            # Read the rest of the lines and group them
            values = []
            for line in file:
                line = line.strip()
                if line.endswith(","):
                    line = line[:-1]
                values.append(line)
            
            # Group values into batches of 10,000
            batch_size = 10000
            for i in range(0, len(values), batch_size):
                batch = values[i:i+batch_size]
                batch_query = f"{insert_statement} {', '.join(batch)};"
                try:
                    cursor.execute(batch_query)  # Execute the batch query
                    db.commit()  # Commit each batch as its own transaction
                    print(f"Batch {i // batch_size + 1} committed successfully.")
                except Exception as batch_error:
                    db.rollback()  # Rollback this batch in case of an error
                    print(f"Error with batch {i // batch_size + 1}: {batch_error}")

    except Exception as e:
        print(f"An overall error occurred: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        db.close()

# Update the file path to the path of your SQL file
file_path = "/Users/jasonmanzara/Documents/ddbs_project/db-generation/user_read.sql"
batch_inserts(file_path)