## join user and article
 
 ### 1
SELECT 
    u.id AS user_id, 
    u.name AS user_name, 
    a.id AS article_id, 
    a.title AS article_title
FROM 
    user u
JOIN 
    article a
ON 
    u.uid = a.aid;
### 2
SELECT 
    U.name        AS user_name,
    U.region      AS user_region,
    A.title       AS article_title,
    A.category    AS article_category,
    R.readTimeLength
FROM user U
JOIN `read` R 
    ON U.uid = R.uid
JOIN article A
    ON A.aid = R.aid;


## With Query Conditions

### 1
SELECT 
    u.id AS user_id, 
    u.name AS user_name, 
    a.id AS article_id, 
    a.title AS article_title
FROM 
    user u
JOIN 
    article a
ON 
    u.uid = a.aid
WHERE 
    u.region = 'Beijing' 
    AND a.category = 'science';

### 2
SELECT 
    u.name AS user_name, 
    r.aid AS article_id, 
    a.title AS article_title
FROM 
    user u
JOIN 
    `read` r ON u.uid = r.uid
JOIN 
    article a ON r.aid = a.aid
WHERE 
    u.dept = 'Computer Science';

### 3
SELECT 
    U.name, 
    U.region,
    A.title,
    A.category,
    R.readTimeLength
FROM user U
JOIN `read` R 
    ON U.uid = R.uid
JOIN article A
    ON A.aid = R.aid
WHERE U.region = 'HongKong'
  AND A.category = 'science';


## populate be read
### 1
INSERT INTO be_read (
    id, timestamp, aid, readNum, readUidList, 
    commentNum, commentUidList, agreeNum, 
    agreeUidList, shareNum, shareUidList, category
)
SELECT 
    NULL AS id, 
    NOW() AS timestamp,
    r.aid, 
    COUNT(r.uid) AS readNum,
    GROUP_CONCAT(r.uid) AS readUidList,
    SUM(CASE WHEN r.commentOrNot THEN 1 ELSE 0 END) AS commentNum,
    GROUP_CONCAT(CASE WHEN r.commentOrNot THEN r.uid ELSE NULL END) AS commentUidList,
    SUM(CASE WHEN r.agreeOrNot THEN 1 ELSE 0 END) AS agreeNum,
    GROUP_CONCAT(CASE WHEN r.agreeOrNot THEN r.uid ELSE NULL END) AS agreeUidList,
    SUM(CASE WHEN r.shareOrNot THEN 1 ELSE 0 END) AS shareNum,
    GROUP_CONCAT(CASE WHEN r.shareOrNot THEN r.uid ELSE NULL END) AS shareUidList,
    a.category
FROM 
    `read` r
JOIN 
    article a ON r.aid = a.aid
GROUP BY 
    r.aid;

### 2
-- Example: Insert 3 new rows into be_read

INSERT INTO be_read (
  id,
  timestamp,
  aid,
  readNum,
  readUidList,
  commentNum,
  commentUidList,
  agreeNum,
  agreeUidList,
  shareNum,
  shareUidList,
  category
)
VALUES
-- Row 1
(101, '2024-01-01 12:00:00',  21,  150, '1001,1002,1003,...', 
                              10,  '1002,1004,...', 
                              20,  '1005,1006,...', 
                              5,   '1007,1008', 
                              'science'),

-- Row 2
(102, '2024-01-01 13:00:00',  42,  90,  '2001,2002,2003,...', 
                              0,   '', 
                              5,   '2008', 
                              2,   '2009,2010', 
                              'technology'),

-- Row 3
(103, '2024-01-02 09:00:00',  84,  300, '3001,3002,3003,...',
                              30,  '3001,3005,3007',
                              50,  '3009,3010,...',
                              10,  '3011,3012,3013',
                              'science');

## popular rank
INSERT INTO popular_rank (
  id,
  timestamp,
  temporalGranularity,
  articleAidList
)
VALUES
(1, '2024-01-01 12:30:00', 'daily', '21,42,84'),
(2, '2024-01-01 12:30:00', 'weekly', '5,10,15'),
...


## query top 5 
### daily
SELECT 
    a.id AS article_id, 
    a.title AS article_title, 
    b.readNum AS total_reads, 
    a.text, 
    a.image, 
    a.video
FROM 
    be_read b
JOIN 
    article a ON b.aid = a.aid
WHERE 
    b.timestamp >= CURDATE()
ORDER BY 
    b.readNum DESC
LIMIT 5;

### weekly
SELECT 
    a.id AS article_id, 
    a.title AS article_title, 
    b.readNum AS total_reads, 
    a.text, 
    a.image, 
    a.video
FROM 
    be_read b
JOIN 
    article a ON b.aid = a.aid
WHERE 
    b.timestamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY 
    b.readNum DESC
LIMIT 5;
### monthly
SELECT 
    a.id AS article_id, 
    a.title AS article_title, 
    b.readNum AS total_reads, 
    a.text, 
    a.image, 
    a.video
FROM 
    be_read b
JOIN 
    article a ON b.aid = a.aid
WHERE 
    b.timestamp >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY 
    b.readNum DESC
LIMIT 5;

### yearly
