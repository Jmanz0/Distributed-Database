#!/usr/bin/env python3

import os
import mysql.connector
from hdfs import InsecureClient

# -------------------------------
#  CONFIGURATION
# -------------------------------
DB_HOST            = "127.0.0.1"   # Vitess/MySQL host
DB_PORT            = 15306         # Vitess/MySQL port
DB_USER            = "user"        # DB user
DB_PASSWORD        = ""            # DB password
DB_NAME            = "dbms"        # or "lookup", etc.

HDFS_NAMENODE_URL  = "http://localhost:50070"  # Adjust to your Hadoop NameNode Web address
HDFS_USER          = "root"       # The Hadoop user for InsecureClient
# -------------------------------

def main():
    # 1) Ask the user which article ID they want
    aid_str = input("Enter the article ID (aid) you want to view media for: ")
    try:
        aid = int(aid_str)
    except ValueError:
        print("Invalid article ID. Exiting.")
        return

    # 2) Connect to MySQL
    db = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    # We'll assume your 'article' table has these columns:
    #   image_paths (TEXT with comma-separated paths)
    #   text_path   (VARCHAR/TEXT, optional)
    #   video_path  (VARCHAR/TEXT, optional)
    # If your columns differ, adjust the SELECT.
    cursor.execute("""
        SELECT image_paths, text_path, video_path
        FROM article
        WHERE aid = %s
    """, (aid,))
    row = cursor.fetchone()

    cursor.close()
    db.close()

    if not row:
        print(f"No article found with aid={aid}. Exiting.")
        return

    # row = (image_paths_csv, text_path, video_path)
    image_paths_csv, text_path, video_path = row

    # Convert CSV to list if not empty
    image_paths = []
    if image_paths_csv:
        image_paths = image_paths_csv.split(",")

    # Build a list of media choices
    # Each entry in 'media_items' is a tuple (label, hdfs_path).
    media_items = []
    # Add text if we have it
    if text_path:
        media_items.append(("Text file", text_path))

    # Add images
    for i, img in enumerate(image_paths, start=1):
        label = f"Image #{i}"
        media_items.append((label, img))

    # Add video if we have it
    if video_path:
        media_items.append(("Video", video_path))

    # If no media found at all:
    if not media_items:
        print("This article has no media paths in the database. Exiting.")
        return

    # 3) Show the user which media items are available
    print("\nAvailable media for this article:")
    for idx, (label, path) in enumerate(media_items, start=1):
        print(f"  {idx}. {label} => {path}")

    # 4) Let the user pick which to view/download
    print("\nChoose which media you want to fetch. Enter multiple numbers comma-separated (e.g. '1,2').")
    choice_str = input("Your choice(s): ").strip()
    if not choice_str:
        print("No choice made. Exiting.")
        return

    # Parse the user input, e.g. "1,2" => [1,2]
    choices = []
    for c in choice_str.split(","):
        c = c.strip()
        try:
            num = int(c)
            if 1 <= num <= len(media_items):
                choices.append(num)
        except ValueError:
            pass  # ignore invalid inputs

    if not choices:
        print("No valid selections. Exiting.")
        return

    # 5) Connect to HDFS
    client = InsecureClient(HDFS_NAMENODE_URL, user=HDFS_USER)

    # 6) For each selected media item, download or view it
    # We'll store all downloaded files under a local 'downloads/article_<aid>' folder
    local_dir = f"downloads/article_{aid}"
    os.makedirs(local_dir, exist_ok=True)

    for choice_num in choices:
        label, hdfs_path = media_items[choice_num - 1]
        # We'll guess file extension from the path
        filename = os.path.basename(hdfs_path)
        local_path = os.path.join(local_dir, filename)

        print(f"\nFetching '{label}' from HDFS path = {hdfs_path}")
        try:
            client.download(hdfs_path, local_path, overwrite=True)
            print(f"Downloaded to local: {local_path}")

            # If it's a text file, maybe we read & print it
            _, ext = os.path.splitext(filename.lower())
            if ext == ".txt":
                with open(local_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                print("\n=== TEXT FILE CONTENT ===")
                print(content)
                print("=========================\n")

        except Exception as e:
            print(f"Error downloading {label}: {e}")

    print("\nDone.")

if __name__ == "__main__":
    main()
