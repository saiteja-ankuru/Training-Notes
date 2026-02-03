-- SQL JOIN QUESTIONS 

-- 1. List all customers along with the films they have rented.
SELECT c.customer_id, c.first_name, c.last_name, f.title
FROM sakila.customer c
JOIN sakila.rental r ON c.customer_id = r.customer_id
JOIN sakila.inventory i ON r.inventory_id = i.inventory_id
JOIN sakila.film f ON i.film_id = f.film_id;

-- 2. List all customers and show their rental count, including those who haven't rented any films.
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(r.rental_id) AS rental_count
FROM sakila.customer c
LEFT JOIN sakila.rental r 
    ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name;

-- 3. Show all films along with their category. Include films that don't have a category assigned.
SELECT 
    f.title,
    cat.name AS category
FROM sakila.film f
LEFT JOIN sakila.film_category fc 
    ON f.film_id = fc.film_id
LEFT JOIN sakila.category cat 
    ON fc.category_id = cat.category_id;

-- 4. Show all customers and staff emails from both customer and staff tables using a full outer join (simulate using LEFT + RIGHT + UNION).
SELECT c.email
FROM sakila.customer c
LEFT JOIN sakila.staff s ON c.email = s.email

UNION

SELECT s.email
FROM sakila.staff s
LEFT JOIN sakila.customer c ON s.email = c.email;

-- 5. Find all actors who acted in the film "ACADEMY DINOSAUR".
SELECT a.first_name, a.last_name
FROM sakila.actor a
JOIN sakila.film_actor fa ON a.actor_id = fa.actor_id
JOIN sakila.film f ON fa.film_id = f.film_id
WHERE f.title = 'ACADEMY DINOSAUR';

-- 6. List all stores and the total number of staff members working in each store, even if a store has no staff.
SELECT 
    s.store_id,
    COUNT(st.staff_id) AS staff_count
FROM sakila.store s
LEFT JOIN sakila.staff st 
    ON s.store_id = st.store_id
GROUP BY s.store_id;

-- 7. List the customers who have rented films more than 5 times. Include their name and total rental count.
SELECT 
    c.first_name,
    c.last_name,
    COUNT(r.rental_id) AS rental_count
FROM sakila.customer c
JOIN sakila.rental r 
    ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(r.rental_id) > 5;
















