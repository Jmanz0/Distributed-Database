

# get started with hadoop and Docker

## Prerequisites
1. Hadoop is running in a Docker container.
2. Data is generated according to the project description:
   - **Article table**: Contains text files, 1-5 images per article, and videos for 5% of articles.
   - The directory structure corresponds to each article having its files grouped in folders.

## Steps to Load Files into HDFS

### Step 1: Generate Data
1. Use the provided Python program to generate the required data.
   - Output includes 10,000 articles with text files, images, and videos.
   - The data will be stored locally in a directory (e.g., `articles/`).

2. Confirm the directory structure. For example:
   ```
   articles/
   ├── article1/
   │   ├── text_a1.txt
   │   ├── image_a1_1.jpg
   │   └── video_a1.mp4
   ├── article2/
   │   ├── text_a2.txt
   │   ├── image_a2_1.jpg
   │   └── image_a2_2.jpg
   ...
   ```

### Step 2: Start Hadoop Services
Ensure that the Hadoop services are running:
```bash
docker-compose up -d
```

### Step 3: Copy Files to the Hadoop Container
1. Copy the locally generated `articles` directory into the Hadoop container:
   docker cp /path/to/articles hadoop-master:/tmp/articles

   Replace `/path/to/articles` with the actual path where your data is stored locally.

2. Verify that the files are copied to the container:

   docker exec -it hadoop-master bash
   ls /tmp/articles

### Step 4: Create a Target Directory in HDFS
1. Inside the container, create a directory in HDFS to store the data:

   hdfs dfs -mkdir /articles


### Step 5: Load Data into HDFS
1. Upload the `articles` directory into HDFS:

   hdfs dfs -put /tmp/articles/* /articles/


2. For large datasets, consider using `hadoop distcp` to enable resumable uploads:

   hadoop distcp file:///tmp/articles hdfs:///articles


### Step 6: Verify the Upload
1. Check that the files are successfully uploaded to HDFS:

   hdfs dfs -ls -R /articles


2. Monitor the space used in HDFS:

   hdfs dfsadmin -report


### Step 7: View Files Using the Hadoop Web UI
1. Open the Hadoop NameNode Web UI in your browser:

   http://<docker-host-ip>:50070

   Replace `<docker-host-ip>` with your Docker host's IP address or `localhost` if running locally.

2. Navigate to **"Utilities > Browse the file system"** to explore the uploaded files under `/articles`.

### Step 8: Monitor Job Progress
For large datasets, monitor the file upload progress using:

hdfs dfsadmin -report

Alternatively, check the progress on the ResourceManager UI:

http://<docker-host-ip>:8088


## Notes
1. Ensure the `mapred-site.xml` configuration file in the container is set correctly with the appropriate `HADOOP_HOME` path.
2. Uploaded files reflect the attributes (text, image, video) in the Article table and are prepared for querying in subsequent tasks.
3. For additional functionality like querying and processing, refer to the project requirements.

## Example Validation Commands
1. List files in HDFS:

   hdfs dfs -ls /articles

2. View the contents of a text file in HDFS:

   hdfs dfs -cat /articles/article1/text_a1.txt
   

# How to connect to kubernetes ------------------------
    Start the docker 
    docker-compose up -d

    check if it is runntig
    docker ps

## achieve connectivity between kubernetes and docker

Option 1: Kubernetes and Docker on the Same Host

    Use host.docker.internal as the hostname in Kubernetes to access services running on Docker.
        Update core-site.xml in Hadoop to:

<property>
    <name>fs.defaultFS</name>
    <value>hdfs://host.docker.internal:9000</value>
</property>

Restart Hadoop to apply changes:

        docker restart hadoop

Option 2: Docker on a Different Host

    Use the IP address or hostname of the Docker host that is reachable from Kubernetes. Update core-site.xml:

<property>
    <name>fs.defaultFS</name>
    <value>hdfs://<docker-host-ip>:9000</value>
</property>

    Replace <docker-host-ip> with the IP address of the Docker host machine.


 ## test the connectivity
 From a Kubernetes pod, check if the Hadoop Namenode is reachable:
    curl http://<docker-host-ip>:50070   

## deploy hadoop client in kubernetes:

apiVersion: v1
kind: Pod
metadata:
  name: hadoop-client
spec:
  containers:
  - name: hadoop-client
    image: bde2020/hadoop-base:2.0.0-hadoop3.2.1-java8
    command: ["sleep", "infinity"]


applying the pod:
kubectl apply -f hadoop-client.yaml


testing the access:
kubectl exec -it hadoop-client -- /bin/bash
hadoop fs -ls hdfs://host.docker.internal:9000/

##integrating media access
hadoop fs -cat hdfs://host.docker.internal:9000/articles/article1/image_a0_0.jpg

### Example: Accessing HDFS Media from MySQL Queries

Combine MySQL article data with HDFS media access using Python:
```python
from hdfs import InsecureClient
import mysql.connector

# HDFS Client
hdfs_client = InsecureClient('http://host.docker.internal:50070', user='hdfs')

# MySQL Connection
db = mysql.connector.connect(host='127.0.0.1', port=15306, user='user', database='dbms')
cursor = db.cursor()

# Fetch Article Metadata
cursor.execute("SELECT title, image_paths FROM article WHERE id=1;")
article = cursor.fetchone()

# Fetch Image from HDFS
with hdfs_client.read(article[1]) as reader:
    data = reader.read()

print(f"Title: {article[0]}\nImage Data: {data[:100]}...")  # Example output
