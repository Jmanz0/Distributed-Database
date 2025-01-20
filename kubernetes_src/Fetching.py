''' HOW TO USE
python fetch_hdfs_or_local.py

enter daily, monthly or weekly

it should show the result in the terminal and give a preview of the media
'''

import os
import mysql.connector
from mysql.connector import Error
from hdfs import InsecureClient
import cv2
import numpy as np

# MySQL Configuration
DB_CONFIG = {
    'host': '127.0.0.1',  # Update to your MySQL host
    'port': 15306,        # Port used in your Kubernetes setup
    'user': 'user',       # Replace with your MySQL username
    'password': '',       # Replace with your MySQL password if applicable
    'database': 'dbms'    # Replace with your database name
}

# HDFS Configuration
HDFS_CLIENT = InsecureClient('http://host.docker.internal:50070', user='hdfs')

# Local Directory for Articles
LOCAL_ARTICLES_DIR = "/Users/wilhelm/Studium/Tsinghua/Distributed_DB_Systems/ddbs_project/db-generation/articles"

def connect_to_db():
    """Establish connection to MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def query_top_articles(granularity='daily'):
    """
    Query top-5 popular articles based on the given granularity (daily, weekly, monthly).
    """
    query = f"""
    SELECT 
        a.id AS article_id, 
        a.title AS article_title, 
        b.readNum AS total_reads, 
        a.text AS text_path, 
        a.image AS image_paths, 
        a.video AS video_path
    FROM 
        be_read b
    JOIN 
        article a ON b.aid = a.aid
    WHERE 
        b.timestamp >= CASE
            WHEN '{granularity}' = 'daily' THEN CURDATE()
            WHEN '{granularity}' = 'weekly' THEN DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            WHEN '{granularity}' = 'monthly' THEN DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        END
    ORDER BY 
        b.readNum DESC
    LIMIT 5;
    """
    try:
        connection = connect_to_db()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
    except Error as e:
        print(f"Query failed: {e}")
        return []

def fetch_media_from_hdfs_or_local(media_type, path):
    """
    Fetch file content from HDFS or Local System.
    """
    if path.startswith("hdfs://"):
        # Fetch from HDFS
        try:
            with HDFS_CLIENT.read(path) as reader:
                return reader.read()
        except Exception as e:
            print(f"Error fetching {media_type} from HDFS: {e}")
            return None
    else:
        # Fetch from Local System
        try:
            local_path = os.path.join(LOCAL_ARTICLES_DIR, path)
            with open(local_path, 'rb') as file:
                return file.read()
        except Exception as e:
            print(f"Error fetching {media_type} from Local: {e}")
            return None

def display_image(image_data):
    """
    Display image using OpenCV.
    """
    image_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is not None:
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error decoding image")

def play_video(video_path):
    """
    Play video using OpenCV.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video")
        return
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Video", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()

def query_top_articles_with_media(granularity='daily'):
    """
    Query top articles and fetch media paths from HDFS or Local System.
    """
    articles = query_top_articles(granularity)
    for article in articles:
        print(f"\nFetching Media for Article: {article['article_title']}")
        
        # Fetch and Display Text
        text_data = None
        if article['text_path']:
            print(f"Fetching text from: {article['text_path']}")
            text_data = fetch_media_from_hdfs_or_local("text", article['text_path'])
            if text_data:
                print(f"Text: {text_data.decode('utf-8')[:500]}...")  # Display first 500 characters of text

        # Fetch and Display Images
        if article['image_paths']:
            image_paths = article['image_paths'].split(",")  # Assume multiple paths are comma-separated
            for image_path in image_paths:
                print(f"Fetching image from: {image_path}")
                image_data = fetch_media_from_hdfs_or_local("image", image_path)
                if image_data:
                    display_image(image_data)

        # Fetch and Play Video
        if article['video_path']:
            print(f"Fetching video from: {article['video_path']}")
            video_data = fetch_media_from_hdfs_or_local("video", article['video_path'])
            if video_data and not article['video_path'].startswith("hdfs://"):
                video_local_path = os.path.join(LOCAL_ARTICLES_DIR, article['video_path'])
                with open(video_local_path, 'wb') as video_file:
                    video_file.write(video_data)
                play_video(video_local_path)

if __name__ == "__main__":
    granularity = input("Enter granularity (daily, weekly, monthly): ").strip().lower()
    query_top_articles_with_media(granularity)
