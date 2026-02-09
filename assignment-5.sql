-- "CTE & WITH" QUERIES (1–6)

-- 1. display all customer details who have made more than 5 payments.
WITH payment_counts AS (
    SELECT
        customer_id,
        COUNT(*) AS payment_count
    FROM sakila.payment
    GROUP BY customer_id
)
SELECT c.*
FROM sakila.customer AS c
JOIN payment_counts AS pc
  ON c.customer_id = pc.customer_id
WHERE pc.payment_count > 5;


-- 2. Find the names of actors who have acted in more than 10 films.
WITH actors_film_count AS (
    SELECT
        actor_id,
        COUNT(*) AS film_count
    FROM sakila.film_actor
    GROUP BY actor_id
)
SELECT a.actor_id, a.first_name, a.last_name, afc.film_count
FROM sakila.actor AS a
JOIN actors_film_count AS afc
  ON a.actor_id = afc.actor_id
WHERE afc.film_count > 10;


-- 3. Find the names of customers who never made a payment.
WITH payment_customers AS (
    SELECT DISTINCT customer_id
    FROM sakila.payment
)
SELECT c.customer_id, c.first_name, c.last_name
FROM sakila.customer AS c
LEFT JOIN payment_customers AS pc
  ON c.customer_id = pc.customer_id
WHERE pc.customer_id IS NULL;


-- 4. List all films whose rental rate is higher than the average rental rate of all films.
WITH average_rental_rate AS (
    SELECT AVG(rental_rate) AS avg_rate
    FROM sakila.film
)
SELECT f.film_id, f.title, f.rental_rate
FROM sakila.film AS f
CROSS JOIN average_rental_rate AS arr
WHERE f.rental_rate > arr.avg_rate;


-- 5. List the titles of films that were never rented.
WITH rented_films AS (
    SELECT DISTINCT i.film_id
    FROM sakila.inventory AS i
    JOIN sakila.rental   AS r
      ON r.inventory_id = i.inventory_id
)
SELECT f.film_id, f.title
FROM sakila.film AS f
LEFT JOIN rented_films AS rf
  ON f.film_id = rf.film_id
WHERE rf.film_id IS NULL;


-- 6. Display the customers who rented films in the same month as customer with ID 5. (year + month match)
WITH months_of_custid5 AS (
    SELECT DISTINCT DATE_FORMAT(rental_date, '%Y-%m') AS ym
    FROM sakila.rental
    WHERE customer_id = 5
),
customers_in_same_month AS (
    SELECT DISTINCT r.customer_id
    FROM sakila.rental AS r
    JOIN months_of_cust5 AS m
      ON DATE_FORMAT(r.rental_date, '%Y-%m') = m.ym
)
SELECT c.customer_id, c.first_name, c.last_name
FROM sakila.customer AS c
JOIN customers_in_same_month AS csm
  ON c.customer_id = csm.customer_id;


-- TEMP TABLE QUERIES (7–12)

-- 7. Find all staff members who handled a payment greater than the average payment amount.
CREATE TEMPORARY TABLE temp_avg_payment AS
SELECT AVG(amount) AS avg_amount
FROM sakila.payment;

CREATE TEMPORARY TABLE temp_staff_gt_avg AS
SELECT DISTINCT p.staff_id
FROM sakila.payment AS p
CROSS JOIN temp_avg_payment AS a
WHERE p.amount > a.avg_amount;

SELECT s.*
FROM sakila.staff AS s
JOIN temp_staff_gt_avg AS t
  ON s.staff_id = t.staff_id;


-- 8. Show the title and rental duration of films whose rental duration is greater than the average.
CREATE TEMPORARY TABLE tmp_avg_duration AS
SELECT AVG(rental_duration) AS avg_duration
FROM sakila.film;

SELECT f.film_id, f.title, f.rental_duration
FROM sakila.film AS f
JOIN tmp_avg_duration AS a
  ON f.rental_duration > a.avg_duration;



-- 9. Find all customers who have the same address as customer with ID 1.
CREATE TEMPORARY TABLE tmp_addr_c1 AS
SELECT address_id
FROM sakila.customer
WHERE customer_id = 1;

SELECT c.*
FROM sakila.customer AS c
JOIN tmp_addr_c1 AS ta
  ON c.address_id = ta.address_id;



-- 10. List all payments that are greater than the average of all payments.
CREATE TEMPORARY TABLE tmp_avg_amount AS
SELECT AVG(amount) AS avg_amount
FROM sakila.payment;

SELECT p.*
FROM sakila.payment AS p
JOIN tmp_avg_amount AS a
  ON p.amount > a.avg_amount;



-- 11. List all customers along with the films they have rented.
CREATE TEMPORARY TABLE tmp_customer_films AS
SELECT
    r.customer_id,
    i.film_id
FROM sakila.rental   AS r
JOIN sakila.inventory AS i
  ON r.inventory_id = i.inventory_id;

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    f.film_id,
    f.title
FROM sakila.customer AS c
JOIN tmp_customer_films AS cf
  ON c.customer_id = cf.customer_id
JOIN sakila.film AS f
  ON cf.film_id = f.film_id;



-- 12. List all customers and show their rental count, including those who haven't rented any films.
CREATE TEMPORARY TABLE tmp_rental_counts AS
SELECT
    customer_id,
    COUNT(*) AS rental_count
FROM sakila.rental
GROUP BY customer_id;

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COALESCE(trc.rental_count, 0) AS rental_count
FROM sakila.customer AS c
LEFT JOIN tmp_rental_counts AS trc
  ON c.customer_id = trc.customer_id;


-- VIEW QUERIES (13–17)

-- 13. Show all films along with their category. Include films that don't have a category assigned.
CREATE VIEW view_film_categories AS
SELECT
    f.film_id,
    f.title,
    c.category_id,
    c.name AS category_name
FROM sakila.film AS f
LEFT JOIN sakila.film_category AS fc
  ON f.film_id = fc.film_id
LEFT JOIN sakila.category AS c
  ON fc.category_id = c.category_id;


-- 14. Show all customers and staff emails from both customer and staff tables using a full outer join (simulate using LEFT + RIGHT + UNION).
CREATE VIEW view_customer_staff_emails AS
SELECT
    c.email AS customer_email,
    NULL AS staff_email
FROM sakila.customer AS c

UNION

SELECT
    NULL AS customer_email,
    s.email AS staff_email
FROM sakila.staff AS s;


-- 15. Find all actors who acted in the film "ACADEMY DINOSAUR".
CREATE VIEW view_actors_academy_dinosaur AS
SELECT
    a.actor_id,
    a.first_name,
    a.last_name
FROM sakila.actor AS a
JOIN sakila.film_actor AS fa
  ON a.actor_id = fa.actor_id
JOIN sakila.film AS f
  ON fa.film_id = f.film_id
WHERE f.title = 'ACADEMY DINOSAUR';


-- 16. List all stores and the total number of staff members working in each store, even if a store has no staff.
CREATE VIEW view_store_staff_counts AS
SELECT
    st.store_id,
    COUNT(s.staff_id) AS staff_count
FROM sakila.store AS st
LEFT JOIN sakila.staff AS s
  ON st.store_id = s.store_id
GROUP BY st.store_id;


-- 17. List the customers who have rented films more than 5 times. Include their name and total rental count.
CREATE VIEW view_customer_rental_counts AS
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(r.rental_id) AS rental_count
FROM sakila.customer AS c
LEFT JOIN sakila.rental AS r
  ON c.customer_id = r.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name;

SELECT *
FROM view_customer_rental_counts
WHERE rental_count > 5;
