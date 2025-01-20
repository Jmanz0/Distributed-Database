'''
need this Columns is first in the DBMS

ALTER TABLE article ADD COLUMN image_paths TEXT;
ALTER TABLE article ADD COLUMN video_path  VARCHAR(255);
ALTER TABLE article ADD COLUMN text_path   VARCHAR(255);


'''

#!/usr/bin/env python3

import os
import re
import mysql.connector

# -------------------------------
#  CONFIGURATION
# -------------------------------
LOCAL_ARTICLES_DIR = "/Users/jasonmanzara/Documents/ddbs_project/db-generation/articles"
HDFS_BASE_PATH     = "/articles"  # We'll store media under /articles/articleXX
DB_HOST            = "127.0.0.1"
DB_PORT            = 15306
DB_USER            = "user"
DB_PASSWORD        = ""
DB_NAME            = "dbms"       # or "lookup", depending on which keyspace
# -------------------------------

def extract_aid_from_folder(folder_name):
    """
    Given a folder name like 'article21', return the integer 21.
    Adjust if your folder naming is different (e.g. 'article_21', etc.).
    Example: "article21" -> 21
    """
    m = re.match(r"article(\d+)$", folder_name)
    if m:
        return int(m.group(1))
    return None

def determine_media_paths(local_dir, article_name):
    """
    Scans the files in `local_dir/article_name` (e.g., article21)
    and returns:
      - a LIST of image paths (all .jpg/.png/.gif)
      - ONE video path (first .mp4/.flv/.mov)
      - ONE text path (first .txt)
    
    We'll store multiple images in a single DB column as comma-separated paths.
    Adapt if you want multiple videos or multiple text files as well.
    """
    local_article_path = os.path.join(local_dir, article_name)
    
    image_paths = []   # collect all images
    video_path  = None
    text_path   = None

    # List all files in the folder
    for fname in os.listdir(local_article_path):
        full_local_path = os.path.join(local_article_path, fname)
        if not os.path.isfile(full_local_path):
            continue  # skip subdirectories, if any

        ext = os.path.splitext(fname)[1].lower()

        # Check if it's an image
        if ext in [".jpg", ".jpeg", ".png", ".gif"]:
            # Build the HDFS path for this file
            hdfs_path = f"{HDFS_BASE_PATH}/{article_name}/{fname}"
            image_paths.append(hdfs_path)

        # Check if it's a video (only store the first one we find)
        elif ext in [".mp4", ".flv", ".mov"] and video_path is None:
            video_path = f"{HDFS_BASE_PATH}/{article_name}/{fname}"

        # Check if it's a text file (only store the first one we find)
        elif ext == ".txt" and text_path is None:
            text_path = f"{HDFS_BASE_PATH}/{article_name}/{fname}"

    return image_paths, video_path, text_path

def main():
    # Connect to MySQL (Vitess)
    db = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    # We assume the 'article' table has columns named:
    #   image_paths (TEXT or VARCHAR) to hold multiple images (CSV),
    #   video_path  (VARCHAR or TEXT) for one video,
    #   text_path   (VARCHAR or TEXT) for one text file
    #
    # If not, you must ALTER TABLE to add them:
    #   ALTER TABLE article ADD COLUMN image_paths TEXT;
    #   ALTER TABLE article ADD COLUMN video_path  VARCHAR(255);
    #   ALTER TABLE article ADD COLUMN text_path   VARCHAR(255);

    # Scan the parent directory for article folders (e.g., "article21")
    for folder_name in os.listdir(LOCAL_ARTICLES_DIR):
        folder_path = os.path.join(LOCAL_ARTICLES_DIR, folder_name)
        if os.path.isdir(folder_path):
            # Try to extract an article ID from the folder name
            aid = extract_aid_from_folder(folder_name)
            if aid is not None:
                # Gather all image paths, plus one video & text
                image_paths_list, video_path, text_path = determine_media_paths(LOCAL_ARTICLES_DIR, folder_name)

                # Convert the list of images to a comma-separated string
                if image_paths_list:
                    image_paths_csv = ",".join(image_paths_list)
                else:
                    image_paths_csv = None  # no images found

                # Build an UPDATE statement for 'article' table
                sql = """
                    UPDATE article
                    SET 
                        image_paths = %s,
                        video_path  = %s,
                        text_path   = %s
                    WHERE aid = %s
                """
                cursor.execute(sql, (image_paths_csv, video_path, text_path, aid))
                db.commit()

                print(f"Updated article (aid={aid}):")
                print(f"  image_paths = {image_paths_csv}")
                print(f"  video_path  = {video_path}")
                print(f"  text_path   = {text_path}")
    
    cursor.close()
    db.close()
    print("Done updating media paths.")

if __name__ == "__main__":
    main()
