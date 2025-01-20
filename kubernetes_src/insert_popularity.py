import mysql.connector
from mysql.connector import errorcode
import random
from datetime import datetime, timedelta

# Database Configuration
DB_CONFIG = {
    'host': '127.0.0.1',  # Update to your MySQL host
    'port': 15306,         # Port used in your Kubernetes setup
    'user': 'user',        # Replace with your MySQL username
    'password': '',        # Replace with your MySQL password if applicable
    'database': 'dbms'     # Replace with your database name
}

# Sample Articles Data (a21 to a30 for demonstration)
# Extend this list up to a173 as needed
articles = [
    ("1506000000021", "a21", 21, "science"),
    ("1506000000022", "a22", 22, "technology"),
    ("1506000000023", "a23", 23, "science"),
    ("1506000000024", "a24", 24, "technology"),
    ("1506000000025", "a25", 25, "science"),
    ("1506000000026", "a26", 26, "technology"),
    ("1506000000027", "a27", 27, "science"),
    ("1506000000028", "a28", 28, "technology"),
    ("1506000000029", "a29", 29, "science"),
    ("1506000000030", "a30", 30, "science"),
    # Add more articles up to a173...
]

def connect_to_database(config):
    """
    Establishes a connection to the MySQL database.
    """
    try:
        conn = mysql.connector.connect(**config)
        print("Successfully connected to the database.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise err

def insert_be_read(conn, articles_data):
    """
    Inserts data into the be_read table.
    """
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO be_read (
            id, timestamp, aid, readNum, readUidList,
            commentNum, commentUidList, agreeNum, agreeUidList,
            shareNum, shareUidList, category
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            readNum = VALUES(readNum),
            readUidList = VALUES(readUidList),
            commentNum = VALUES(commentNum),
            commentUidList = VALUES(commentUidList),
            agreeNum = VALUES(agreeNum),
            agreeUidList = VALUES(agreeUidList),
            shareNum = VALUES(shareNum),
            shareUidList = VALUES(shareUidList),
            category = VALUES(category);
    """

    # Generate a base date for timestamps
    base_date = datetime.strptime('2024-12-01', '%Y-%m-%d')

    be_read_records = []
    for idx, article in enumerate(articles_data):
        id_str, aid_str, aid, category = article
        id = int(id_str)
        # Assign a unique date for each article for demonstration purposes
        # In a real scenario, the timestamp should reflect actual read dates
        timestamp = (base_date + timedelta(days=idx)).strftime('%Y-%m-%d')

        # Simulate readNum and other metrics
        readNum = random.randint(50, 500)
        readUidList = ','.join([str(random.randint(1, 1000)) for _ in range(random.randint(3, 10))])
        commentNum = random.randint(10, 200)
        commentUidList = ','.join([str(random.randint(1, 1000)) for _ in range(random.randint(3, 10))])
        agreeNum = random.randint(20, 300)
        agreeUidList = ','.join([str(random.randint(1, 1000)) for _ in range(random.randint(3, 10))])
        shareNum = random.randint(5, 100)
        shareUidList = ','.join([str(random.randint(1, 1000)) for _ in range(random.randint(2, 5))])

        be_read_records.append((
            id, timestamp, aid, readNum, readUidList,
            commentNum, commentUidList, agreeNum, agreeUidList,
            shareNum, shareUidList, category
        ))

    try:
        cursor.executemany(insert_query, be_read_records)
        conn.commit()
        print(f"Inserted/Updated {cursor.rowcount} records into be_read table.")
    except mysql.connector.Error as err:
        print(f"Error inserting into be_read: {err}")
        conn.rollback()
    finally:
        cursor.close()

def generate_popular_rank(conn):
    """
    Generates and inserts popular rankings into the popular_rank table.
    Assumes popular_rank entries are daily rankings based on readNum.
    """
    cursor = conn.cursor()
    # Define the temporal granularity
    temporal_granularity = 'daily'

    # Select distinct timestamps from be_read
    select_dates_query = "SELECT DISTINCT timestamp FROM be_read;"
    try:
        cursor.execute(select_dates_query)
        dates = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching distinct dates: {err}")
        cursor.close()
        return

    popular_rank_records = []
    rank_id = 1  # Starting ID for popular_rank

    for date_tuple in dates:
        date = date_tuple[0]
        # Select top 5 articles based on readNum for the given date
        select_top_articles_query = """
            SELECT aid FROM be_read
            WHERE timestamp = %s
            ORDER BY readNum DESC
            LIMIT 5;
        """
        try:
            cursor.execute(select_top_articles_query, (date,))
            top_articles = cursor.fetchall()
            article_aid_list = ','.join([str(article[0]) for article in top_articles])
            if not article_aid_list:
                continue  # Skip if no articles found for the date

            popular_rank_records.append((
                rank_id, date, temporal_granularity, article_aid_list
            ))
            rank_id += 1
        except mysql.connector.Error as err:
            print(f"Error fetching top articles for date {date}: {err}")

    # Insert popular_rank records
    if popular_rank_records:
        insert_query = """
            INSERT INTO popular_rank (id, timestamp, temporalGranularity, articleAidList)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                temporalGranularity = VALUES(temporalGranularity),
                articleAidList = VALUES(articleAidList);
        """
        try:
            cursor.executemany(insert_query, popular_rank_records)
            conn.commit()
            print(f"Inserted/Updated {cursor.rowcount} records into popular_rank table.")
        except mysql.connector.Error as err:
            print(f"Error inserting into popular_rank: {err}")
            conn.rollback()
    else:
        print("No popular_rank records to insert.")

    cursor.close()

def main():
    # Connect to the database
    conn = connect_to_database(DB_CONFIG)

    try:
        # Insert data into be_read table
        insert_be_read(conn, articles)

        # Generate and insert popular_rank data
        generate_popular_rank(conn)

    finally:
        # Close the database connection
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()