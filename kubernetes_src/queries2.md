## Retrieve all users:

SELECT * 
FROM user;

SELECT * 
FROM user
WHERE dept = 'dept17'
  AND region = 'HongKong';

# sharding ex 
USE `dbms:-80`;

## Retrieve all articles

SELECT * 
FROM article;

SELECT * 
FROM article
WHERE category = 'science'
  AND language = 'en';

## Read table

SELECT * 
FROM `read`
LIMIT 10000;

SELECT * 
FROM `read`
WHERE readTimeLength = 1
  AND agreeOrNot = TRUE;
LIMIT 10000;

## users and article join:
SELECT 
    u.name AS user_name, 
    a.title AS article_title
FROM user u
JOIN article a 
ON u.dept = 'dept17'
WHERE a.category = 'science' 
  AND a.language = 'en'
  AND a.aid BETWEEN 100 AND 1000;


USE `dbms:-80`;
USE `dbms:80-`;

# Remove data from USERS 
DELETE FROM users;
mysql < /Users/jasonmanzara/Documents/ddbs_project/db-generation/user.sql

# Update
UPDATE user
SET email = CONCAT('up_', email)
WHERE gender='male';