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

-- one to one
-- user to user profile

-- one to many
-- user to orders

-- many to one
-- orders to user

-- many to many
