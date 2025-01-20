## Prereqs:
Before we get started, let’s get a few pre-requisites out of the way:

Install Docker Engine locally.

Install Minikube and start a Minikube engine:

minikube start --kubernetes-version=v1.28.5 --cpus=4 --memory=11000 --disk-size=32g

for Willis System:
minikube start --kubernetes-version=v1.31.0 --cpus=4 --memory=3200 --disk-size=32g 

Allocating less memory than specified will cause crashes in subsequent steps and break the process
Install kubectl and ensure it is in your PATH.

Install the MySQL client locally.

Install vtctldclient locally.

Copied from: https://vitess.io/docs/21.0/get-started/operator/

# Step 1:

kubectl apply -f operator.yaml
kubectl apply -f example-cluster-config.yaml
kubectl apply -f vitesscluster.yaml

(Please wait until all services are running -- check with `kubectl get pods`)

## Step 2: port forward
./pf.sh

<!-- alias vtctldclient="vtctldclient --server=localhost:15999" -->

## step 3: Apply schemas
./vtctldclient --server=localhost:15999 ApplySchema --sql-file="./schema/lookup_tables.sql" lookup
./vtctldclient --server=localhost:15999 ApplyVSchema --vschema-file="./vschema/lookup_vschema.json" lookup

./vtctldclient --server=localhost:15999 ApplySchema --sql-file="./schema/dbms/create_tables.sql" dbms
./vtctldclient --server=localhost:15999 ApplyVSchema --vschema-file="./vschema/dbms_vschema.json" dbms

## Step 4: Connect to cluster
alias mysql="mysql -h 127.0.0.1 -P 15306 -u user"
mysql

## checking health
kubectl get pods
kubectl get svc 
kubectl get pvc 
kubectl get pv

# logs
kubectl logs <service>

## steps to remove
kubectl delete -f operator.yaml

## access mysql
mysql

## Access to Web ui
127.0.0.1:14000


## select specific shard
USE `dbms:-80`;
USE `dbms:80-`;

### Todo
1) Duplication across shards (directly insert to second shard)
2) Update lookup tables for article + user (requires a read from the database, and a entry)
    a. Insert into lookup table


## Running the scripts:
mysql < /Users/jasonmanzara/Documents/ddbs_project/db-generation/article.sql
mysql < /Users/jasonmanzara/Documents/ddbs_project/db-generation/user.sql

<!-- mysql < /Users/jasonmanzara/Documents/ddbs_project/db-generation/user_read.sql -->