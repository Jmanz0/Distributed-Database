#!/usr/bin/env bash

# Start SSH (required by Hadoop)
service ssh start

# Start HDFS daemons
$HADOOP_HOME/sbin/start-dfs.sh

# Start YARN daemons
$HADOOP_HOME/sbin/start-yarn.sh

# Keep container running
tail -f /dev/null
