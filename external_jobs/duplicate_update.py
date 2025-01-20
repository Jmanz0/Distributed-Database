import time
import mysql.connector

def move_science_articles_and_beread():
    while True:
        try:
            # Connect to shard1
            shard1_db = mysql.connector.connect(
                host="127.0.0.1",
                port=15306,
                user="user",
                password="",
                database="dbms:-80"
            )
            shard1_cursor = shard1_db.cursor()

            # Connect to shard2
            shard2_db = mysql.connector.connect(
                host="127.0.0.1",
                port=15306,
                user="user",
                password="",
                database="dbms:80-"
            )
            shard2_cursor = shard2_db.cursor()

            # Move articles from shard1 to shard2
            shard1_cursor.execute(
                """
                SELECT id, timestamp, aid, category, title, abstract, articleTags, authors, language, text, image, video, processed
                FROM article
                WHERE category = 'science' AND processed_duplicate = FALSE
                LIMIT 5000
                """
            )
            articles = shard1_cursor.fetchall()

            for article in articles:
                shard2_cursor.execute(
                    """
                    INSERT INTO article (id, timestamp, aid, category, title, abstract, articleTags, authors, language, text, image, video, processed, processed_duplicate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE
                    title = VALUES(title), abstract = VALUES(abstract), timestamp = VALUES(timestamp),
                    articleTags = VALUES(articleTags), authors = VALUES(authors), language = VALUES(language),
                    text = VALUES(text), image = VALUES(image), video = VALUES(video), processed = VALUES(processed),
                    processed_duplicate = TRUE
                    """, article
                )
            shard2_db.commit()

            # Update shard1 processed flags
            shard1_cursor.execute(
                "UPDATE article SET processed = TRUE, processed_duplicate = TRUE WHERE category = 'science' AND processed_duplicate = FALSE"
            )
            shard1_db.commit()

            # Move `be_read` records from shard1 to shard2
            shard1_cursor.execute(
                """
                SELECT b.id, b.aid, b.readNum, b.readUidList, b.commentNum, b.commentUidList,
                       b.agreeNum, b.agreeUidList, b.shareNum, b.shareUidList, b.category
                FROM be_read AS b
                INNER JOIN article AS a ON b.aid = a.aid
                WHERE a.category = 'science' AND a.processed_duplicate = FALSE
                LIMIT 5000
                """
            )
            be_read_records = shard1_cursor.fetchall()

            for record in be_read_records:
                shard2_cursor.execute(
                    """
                    INSERT INTO be_read (id, aid, readNum, readUidList, commentNum, commentUidList, agreeNum,
                                         agreeUidList, shareNum, shareUidList, category, processed_duplicate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE
                    readNum = VALUES(readNum), readUidList = VALUES(readUidList),
                    commentNum = VALUES(commentNum), commentUidList = VALUES(commentUidList),
                    agreeNum = VALUES(agreeNum), agreeUidList = VALUES(agreeUidList),
                    shareNum = VALUES(shareNum), shareUidList = VALUES(shareUidList),
                    category = VALUES(category), processed_duplicate = TRUE
                    """, record
                )
            shard2_db.commit()

            print("Moved new science articles and associated `be_read` records successfully.")
            time.sleep(10)

        except mysql.connector.Error as err:
            print(f"MySQL error: {err}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if shard1_cursor and shard1_db.is_connected():
                shard1_cursor.close()
                shard1_db.close()
            if shard2_cursor and shard2_db.is_connected():
                shard2_cursor.close()
                shard2_db.close()

if __name__ == "__main__":
    move_science_articles_and_beread()