-----------------------------------------
#Substring 
SELECT title, SUBSTRING(title, 1, 3) AS short_title 
FROM sakila.film;

----------------------
#concatination

SELECT CONCAT(first_name, '@ ', last_name) AS full_name 
FROM sakila.customer;

------------------------------
#length 

SELECT title, LENGTH(title) AS title_length 
FROM sakila.film 
WHERE LENGTH(title) > 15;
--------------------------------------
#substring with locate 
select email from sakila.customer;
SELECT email,
       SUBSTRING(email, LOCATE('@', email)+1) AS domain
FROM sakila.customer;

SELECT 
  email,
  substring_index(SUBSTRING(email, LOCATE('@', email) + 1), '.', 1) AS domain
FROM 
  sakila.customer;
  
select substring_index(email,'@', -1) from sakila.customer;

--------------------------
SELECT title
FROM sakila.film
WHERE UPPER(title) LIKE '%LOVELY%' OR UPPER(title) LIKE '%MAN';

select title, lower(title) as lower_titles
FROM sakila.film;
--------------------------------------------------
SELECT LEFT(title, 1) AS first_letter, right(title,1) as last_letter, COUNT(*) AS film_count
FROM sakila.film
GROUP BY LEFT(title, 1), right(title,1) 
ORDER BY film_count DESC;
-----
SELECT LEFT(title,1) AS first_letter, right(title, 1) as last_letter, title 
from sakila.film;

-------------------
SELECT last_name,
       CASE 
           WHEN LEFT(last_name, 1) BETWEEN 'A' AND 'M' THEN 'Group A-M'
           WHEN LEFT(last_name, 1) BETWEEN 'N' AND 'Z' THEN 'Group N-Z'
           ELSE 'Other'
       END AS group_label
FROM sakila.customer;

---------------

SELECT title, REPLACE(title, 'A', 'x') AS cleaned_title
FROM sakila.film
WHERE title LIKE '% ' '%';

-----------------
SELECT customer_id, last_name
FROM sakila.customer
WHERE last_name REGEXP '[^aeiouAEIOU]{3}'; -- decode

SELECT title
FROM sakila.film
WHERE title REGEXP '[aeiouAEIOU]$';

select right(title,1), count(*)
FROM sakila.film
WHERE title REGEXP '[aeiouAEIOU]$'
group by right(title,1)
;
--------------------------------
#math 

SELECT title, rental_rate, rental_rate * 2 AS double_rate
FROM sakila.film;
------------------------
---------------
#math 

SELECT customer_id,
       COUNT(payment_id) AS payments,
       SUM(amount) AS total_paid,
       SUM(amount) / COUNT(payment_id) AS avg_payment
FROM sakila.payment
GROUP BY customer_id;
------------

ALTER TABLE sakila.film
ADD COLUMN cost_efficiency DECIMAL(6,2);


UPDATE sakila.film
SET cost_efficiency = replacement_cost / length
WHERE length IS NOT NULL;


select * from sakila.film;
---------------------------------
#date diff 

SELECT rental_id, DATEDIFF(return_date, rental_date) AS days_rented
FROM sakila.rental
WHERE return_date IS NOT NULL;

#date time 

select month(last_update) from sakila.film;

SELECT payment_date FROM sakila.payment;

SELECT DATE(payment_date) AS pay_date, SUM(amount) AS total_paid
FROM sakila.payment
GROUP BY DATE(payment_date)
ORDER BY pay_date DESC;

#Find Customers Who Paid in the Last 24 Hours

select * from sakila.payment;

SELECT customer_id, amount, payment_date
FROM sakila.payment
WHERE payment_date >= NOW() - INTERVAL 1 DAY;

select max(payment_date) FROM sakila.payment;

SELECT customer_id, amount, payment_date
FROM sakila.payment
WHERE payment_date >= (
    SELECT MAX(payment_date) - INTERVAL 1 day
    FROM sakila.payment
);

select now()  - INTERVAL 1 DAY as yesterday;


SELECT CONCAT('Today is: ', CURDATE()) AS message;
SELECT CONCAT('Today is: ', now()) AS message;

SELECT NOW(), CURDATE(), CURRENT_TIME;

--------------------------------------------------------
#sub queries 

SELECT first_name, last_name
FROM sakila.customer

WHERE address_id IN (
    SELECT address_id
    FROM sakila.customer
     #WHERE customer_id = 1
);

-----------------------------------
SELECT actor_id, first_name, last_name
FROM sakila.actor
WHERE actor_id IN (
    SELECT actor_id
    FROM sakila.film_actor
    GROUP BY actor_id
    HAVING COUNT(film_id) > 10
);


------------------
#sub query in  select 

SELECT actor_id,
       first_name,
       last_name,
       (
           SELECT COUNT(*)
           FROM sakila.film_actor
           WHERE film_actor.actor_id = actor.actor_id
       ) AS film_count
FROM sakila.actor;

------------------------
# Derived Tables

SELECT a.actor_id, a.first_name, a.last_name, fa.film_count
FROM sakila.actor a
JOIN (
    SELECT actor_id, COUNT(film_id) AS film_count
    FROM sakila.film_actor
    GROUP BY actor_id
    HAVING COUNT(film_id) > 10
) fa ON a.actor_id = fa.actor_id;


SELECT customer_id, total_spent
FROM (
    SELECT customer_id, SUM(amount) AS total_spent
    FROM sakila.payment
    GROUP BY customer_id
    ORDER BY total_spent DESC
    LIMIT 5
) AS top_customers;


SELECT *
FROM (
    SELECT last_name,
           CASE 
               WHEN LEFT(last_name, 1) BETWEEN 'A' AND 'M' THEN 'Group A-M'
               WHEN LEFT(last_name, 1) BETWEEN 'N' AND 'Z' THEN 'Group N-Z'
               ELSE 'Other'
           END AS group_label
    FROM sakila.customer
) AS grouped_customers 
WHERE group_label = 'Group N-Z';

# order of execution 
 -- FROM ---- > Where --->  select 

---------------------------------
-- Use subqueries when:
-- You need temporary results to build your main query
-- You are comparing against aggregate values

SELECT customer_id, amount
FROM sakila.payment
WHERE amount > (
    SELECT AVG(amount)
    FROM sakila.payment
);
#when sub query fail 

SELECT first_name,
       (SELECT address_id FROM sakila.address WHERE district = 'California'  ) AS cali_address
FROM sakila.customer;
------------------------------------------------
#co related subqueries 
-- A correlated subquery is a subquery that:
-- Refers to a column from the outer (main) query
-- Is executed once for each row in the outer query
SELECT title,
  (SELECT COUNT(*)
   FROM sakila.film_actor fa
   WHERE fa.film_id = f.film_id) AS actor_count
FROM sakila.film f;
-------------------------------

SELECT payment_id, customer_id, amount, payment_date
FROM sakila.payment p1
WHERE amount > (
    SELECT AVG(amount)
    FROM sakila.payment p2
    WHERE p2.customer_id = p1.customer_id
);
select amount from sakila.customer;