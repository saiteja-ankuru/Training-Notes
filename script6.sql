SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(p.amount) AS total_spent
FROM sakila.customer AS c
JOIN sakila.payment AS p 
    ON p.customer_id = c.customer_id
GROUP BY 
    c.customer_id, c.first_name, c.last_name
HAVING 
    total_spent > (
        SELECT AVG(customer_total)
        FROM (
            SELECT 
                SUM(p2.amount) AS customer_total
            FROM sakila.payment AS p2
            GROUP BY p2.customer_id
        ) AS t
    );
    
WITH customer_totals AS (
    SELECT 
        customer_id,
        SUM(amount) AS total_spent
    FROM sakila.payment
    GROUP BY customer_id
)

SELECT 
    ct.customer_id,
    c.first_name,
    c.last_name,
    ct.total_spent
FROM customer_totals AS ct
JOIN sakila.customer AS c 
    ON c.customer_id = ct.customer_id
WHERE ct.total_spent > (
    SELECT AVG(total_spent) 
    FROM customer_totals
);


#CTE
-- A CTE (Common Table Expression) is a temporary result set that you can reference within a SELECT, INSERT, UPDATE, or DELETE query.
-- readable , re usable

SELECT customer_id, total_payments
FROM (
    SELECT customer_id, COUNT(*) AS total_payments
    FROM sakila.payment
    GROUP BY customer_id
) AS sub
WHERE total_payments > 5
;

----------------
WITH payment_counts AS (
    SELECT customer_id, COUNT(*) AS total_payments
    FROM sakila.payment
    GROUP BY customer_id
)
SELECT customer_id, total_payments
FROM payment_counts
WHERE total_payments > 5;


WITH payment_counts AS (
    SELECT customer_id, COUNT(*) AS total_payments
    FROM sakila.payment
    GROUP BY customer_id
)
SELECT c.customer_id, c.first_name, c.last_name, p.total_payments
FROM sakila.customer c
JOIN payment_counts p ON c.customer_id = p.customer_id
WHERE p.total_payments > 5;


--------------------------------------------------------------------
WITH total_payments AS (
    SELECT customer_id, SUM(amount) AS total_amount
    FROM sakila.payment
    GROUP BY customer_id
),
latest_payment AS (
    SELECT customer_id, MAX(payment_date) AS last_payment_date
    FROM sakila.payment
    GROUP BY customer_id
)
SELECT c.customer_id, c.first_name, c.last_name,
       tp.total_amount,
       lp.last_payment_date
FROM sakila.customer c
LEFT JOIN total_payments tp ON c.customer_id = tp.customer_id
LEFT JOIN latest_payment lp ON c.customer_id = lp.customer_id;

-----------

    
----------------------------------
WITH RECURSIVE numbers AS (
  -- Step 1: Anchor member (starting row)
  SELECT 1 AS n

  UNION ALL

  -- Step 2: Recursive member (generate next number)
  SELECT n + 1
  FROM numbers
  WHERE n < 20
) 
SELECT * FROM numbers;


------

-- Recursive CTE to generate the last 10 days
WITH RECURSIVE dates AS (
  SELECT DATE(MAX(rental_date)) - INTERVAL 9 DAY AS rental_day
  FROM sakila.rental
  UNION ALL
  SELECT rental_day + INTERVAL 1 DAY
  FROM dates
  WHERE rental_day + INTERVAL 1 DAY <= (SELECT MAX(rental_date) FROM sakila.rental)
)
SELECT d.rental_day, COUNT(r.rental_id) AS rentals
FROM dates d
LEFT JOIN sakila.rental r ON DATE(r.rental_date) = d.rental_day
GROUP BY d.rental_day;

------------------------------------------
select date(rental_date), count(*)
from sakila.rental 
where date(rental_date) = '2006-02-14'
group by date(rental_Date);
----------------------------------

-- SELECT a.actor_id, a.first_name, a.last_name
-- FROM sakila.actor a
-- JOIN sakila.film_actor fa ON a.actor_id = fa.actor_id
-- JOIN sakila.film f ON fa.film_id = f.film_id
-- WHERE f.title = 'ACADEMY DINOSAUR';

------------------------------------
-- TEMPORARY TABLES
-- ##################################
-- A table that exists only for the session or until explicitly dropped.
-- Useful for storing intermediate results or testing transformations without affecting actual data

-- Top 5 most rented categories
DROP TEMPORARY TABLE IF EXISTS sakila.top_categories;

CREATE TEMPORARY TABLE sakila.top_categories AS
SELECT c.name AS category_name,c.category_id, COUNT(*) AS rental_count
FROM sakila.rental r
JOIN sakila.inventory i ON r.inventory_id = i.inventory_id
JOIN sakila.film f ON f.film_id = i.film_id
JOIN sakila.film_category fc ON f.film_id = fc.film_id
JOIN sakila.category c ON c.category_id = fc.category_id
GROUP BY c.name,c.category_id
ORDER BY rental_count DESC
LIMIT 5;


SELECT * FROM 
sakila.top_categories tc 
join sakila.film_category fc
on fc.category_id = tc.category_id
 ;

select tc.category_name, tc.category_id from sakila.top_categories tc
join sakila.category c 
on c.category_id = tc.category_id
;


-- VIEWS
-- ##################################
-- A virtual table created using a stored SQL query.
-- Helps with simplifying complex queries, data abstraction, and security (limit what users can see).
-- View for customer’s most recent rental

drop view sakila.recent_rentals; 

CREATE OR REPLACE VIEW sakila.recent_rentals AS
SELECT r.customer_id as cstd_id, MAX(r.rental_date) AS ruchik
FROM sakila.rental r
GROUP BY r.customer_id;

select * from sakila.recent_rentals;

SELECT c.first_name, c.last_name, rr.ruchik
FROM sakila.customer c
JOIN sakila.recent_rentals rr ON c.customer_id = rr.customer_id;

-- Public view hiding sensitive columns
CREATE OR REPLACE VIEW sakila.customer_public_view AS
SELECT customer_id, first_name, last_name, email
FROM sakila.customer;

SELECT * FROM sakila.customer_public_view;

SELECT customer_id, first_name, last_name, email
FROM sakila.customer;





