import time
import mysql.connector

def update_lookup_tables():
    try:
        db = mysql.connector.connect(
            host="127.0.0.1",
            port=15306,
            user="user",
            password="",
            database="dbms"
        )
        cursor = db.cursor()

        while True:
            cursor.execute(
                """
                SELECT u.uid, rl.keyspace_id
                FROM user u
                JOIN lookup.region_lookup rl
                ON u.region = rl.region
                WHERE u.processed = FALSE
                LIMIT 2000
                """
            )
            users = cursor.fetchall()

            for uid, keyspace_id in users:
                cursor.execute(
                    "INSERT INTO lookup.uid_lookup (uid, keyspace_id) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE keyspace_id = VALUES(keyspace_id)",
                    (uid, keyspace_id)
                )

                cursor.execute(
                    "UPDATE user SET processed = TRUE WHERE uid = %s",
                    (uid,)
                )

            cursor.execute(
                """
                SELECT a.aid, cl.keyspace_id
                FROM article a
                JOIN lookup.category_lookup cl
                ON a.category = cl.category
                WHERE a.processed = FALSE
                LIMIT 2000
                """
            )
            articles = cursor.fetchall()

            for aid, keyspace_id in articles:
                cursor.execute(
                    "INSERT INTO lookup.aid_lookup (aid, keyspace_id) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE keyspace_id = VALUES(keyspace_id)",
                    (aid, keyspace_id)
                )

                cursor.execute(
                    "UPDATE article SET processed = TRUE WHERE aid = %s",
                    (aid,)
                )

            db.commit()

            print(f"Processed {len(users)} users and {len(articles)} articles.")
            time.sleep(2) 

    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    update_lookup_tables()