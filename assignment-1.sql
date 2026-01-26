-- SQL Practice Questions
---------------------------------

-- 1. Get all customers whose first name starts with 'J' and who are active.
SELECT *
FROM sakila.customer
WHERE first_name LIKE 'J%'
  AND active = 1;

-- 2. Find all films where the title contains the word 'ACTION' or the description contains 'WAR'.
SELECT *
FROM sakila.film
WHERE title LIKE '%ACTION%'
   OR description LIKE '%WAR%';

-- 3. List all customers whose last name is not 'SMITH' and whose first name ends with 'a'.
SELECT *
FROM sakila.customer
WHERE last_name <> 'SMITH'
  AND first_name LIKE '%a';

-- 4. Get all films where the rental rate is greater than 3.0 and the replacement cost is not null.
SELECT *
FROM sakila.film
WHERE rental_rate > 3.0
  AND replacement_cost IS NOT NULL;

-- 5. Count how many customers exist in each store who have active status = 1.
SELECT store_id, COUNT(*) AS active_customers
FROM sakila.customer
WHERE active = 1
GROUP BY store_id;

-- 6. Show distinct film ratings available in the film table.
SELECT DISTINCT rating
FROM sakila.film;

-- 7. Find the number of films for each rental duration where the average length is more than 100 minutes.
SELECT rental_duration, AVG(length) AS avg_length
FROM sakila.film
GROUP BY rental_duration
HAVING AVG(length) > 100;

-- 8. List payment dates and total amount paid per date, but only include days where more than 100 payments were made.
SELECT DATE(payment_date) AS payment_day,
       SUM(amount) AS total_amount
FROM sakila.payment
GROUP BY DATE(payment_date)
HAVING COUNT(*) > 100;

-- 9. Find customers whose email address is null or ends with '.org'.
SELECT *
FROM sakila.customer
WHERE email IS NULL
   OR email LIKE '%.org';

-- 10. List all films with rating 'PG' or 'G', and order them by rental rate in descending order.
SELECT title, rating, rental_rate
FROM sakila.film
WHERE rating IN ('PG', 'G')
ORDER BY rental_rate DESC;

-- 11. Count how many films exist for each length where the film title starts with 'T' and the count is more than 5.
SELECT length, COUNT(*) AS film_count
FROM sakila.film
WHERE title LIKE 'T%'
GROUP BY length
HAVING COUNT(*) > 5;

-- 12. List all actors who have appeared in more than 10 films.
SELECT a.actor_id, a.first_name, a.last_name, COUNT(*) AS film_count
FROM sakila.actor a
JOIN sakila.film_actor fa ON a.actor_id = fa.actor_id
GROUP BY a.actor_id
HAVING COUNT(*) > 10;

-- 13. Find the top 5 films with the highest rental rates and longest lengths combined, ordering by rental rate first and length second.
SELECT title, rental_rate, length
FROM sakila.film
ORDER BY rental_rate DESC, length DESC
LIMIT 5;

-- 14. Show all customers along with the total number of rentals they have made, ordered from most to least rentals.
SELECT c.customer_id, c.first_name, c.last_name,
       COUNT(r.rental_id) AS total_rentals
FROM sakila.customer c
LEFT JOIN sakila.rental r ON c.customer_id = r.customer_id
GROUP BY c.customer_id
ORDER BY total_rentals DESC;

-- 15. List the film titles that have never been rented.
SELECT f.title
FROM sakila.film f
LEFT JOIN sakila.inventory i ON f.film_id = i.film_id
LEFT JOIN sakila.rental r ON i.inventory_id = r.inventory_id
WHERE r.rental_id IS NULL;
