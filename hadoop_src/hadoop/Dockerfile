FROM openjdk:8-jdk

ENV HADOOP_VERSION=3.4.1
ENV HADOOP_HOME=/opt/hadoop
ENV JAVA_HOME=/usr/local/openjdk-8
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Install dependencies including sudo
RUN apt-get update && apt-get install -y curl ssh rsync sudo && rm -rf /var/lib/apt/lists/*

# Download and extract Hadoop
RUN curl -sSL https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    | tar -xz -C /opt && \
    mv /opt/hadoop-${HADOOP_VERSION} $HADOOP_HOME && \
    rm -rf $HADOOP_HOME/share/doc && \
    mkdir -p $HADOOP_HOME/hdfs/namenode && \
    mkdir -p $HADOOP_HOME/hdfs/datanode

# Configure SSH for Hadoop's internal communication
RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -P '' && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

# Copy configuration files
COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
COPY yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml
COPY mapred-site.xml $HADOOP_HOME/etc/hadoop/mapred-site.xml

# Set JAVA_HOME in hadoop-env.sh so Hadoop recognizes it
RUN echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Format HDFS namenode
RUN $HADOOP_HOME/bin/hdfs namenode -format

# Copy startup script
COPY start-hadoop.sh /start-hadoop.sh
RUN chmod +x /start-hadoop.sh

EXPOSE 50070 8088 8020 9000 9864 9866

CMD ["/start-hadoop.sh"]
