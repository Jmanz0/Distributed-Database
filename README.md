# Project Overview

<img width="1054" alt="Screenshot 2025-01-19 at 9 01 34 PM" src="https://github.com/user-attachments/assets/08ca8b3d-97b0-4307-8210-0081bc98081d" />

## Project Goals
1) Horizontally Shard the Database in these following ways:
   a) Fragmentation of SQL Table based on specific field attributes (i.e category = "Beijing" and category = "Shanghai")
   b) Duplication of tables across fragments
   c) Fragmentation of alternate SQL Table dependent on specific field attribute in another table (i.e Must query other table to find location of the shard)
2) Replication
3) Failover

TODO: Still under progress of writing, please look at the database_report for more details
