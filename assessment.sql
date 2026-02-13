-- 1. Create CTE to fetch customers with rentals >= 30
WITH rentals_gt30 AS(
	select customer_id, count(*) as count
    from sakila.rental r
    group by customer_id
    having count(*) >= 30
)

select c.*, rg.count
from sakila.customer c
join rentals_gt30 rg on c.customer_id = rg.customer_id;

-- -------------------------------------------------------
select c.*, count(*)
from sakila.customer c
join sakila.rental r on c.customer_id=r.customer_id
group by c.customer_id
having count(*) >= 30;


-- 2. Using CTE fetch top 5 categories by rental count
with top_categories as(
	select cat.category_id, cat.name,  COUNT(r.rental_id) AS rental_count
    from sakila.category cat
	join sakila.film_category fc on cat.category_id = fc.category_id
	join sakila.film f on fc.film_id = f.film_id
	join sakila.inventory i on f.film_id = i.film_id
	join sakila.rental r on i.inventory_id = r.inventory_id
    GROUP BY cat.category_id, cat.name
)

select *
from top_categories
order by rental_count desc
limit 5;


-- 3. customers who rented atleast 1 PG rating film
select c.customer_id, c.first_name, c.last_name, count(f.rating) as count
from sakila.customer c
join sakila.rental r on c.customer_id = r.customer_id
join sakila.inventory i on r.inventory_id = i.inventory_id
join sakila.film f on i.film_id = f.film_id
where f.rating = "PG"
group by c.customer_id,  c.first_name, c.last_name
having count(f.rating) >= 1;


-- 4. get the films in action category
select f.title, cat.name
from sakila.film f
join sakila.film_category fc on f.film_id = fc.film_id
join sakila.category cat on fc.category_id = cat.category_id
where cat.name = "Action";

with action_cat as (
	select cat.name, fc.film_id
    from sakila.category cat
    join sakila.film_category fc on cat.category_id = fc.category_id
    where cat.name = "Action"
)

select f.title from sakila.film f
join action_cat ac on f.film_id = ac.film_id;


-- 5. films longer than average film length
with average_length as (
	select avg(f.length) as avg_len
    from sakila.film f
)
 select f.title, length, al.avg_len
 from sakila.film f
 cross join average_length al
 where f.length > al.avg_len;
 
select title 
from sakila.film
where length > (select avg(length) from sakila.film);


-- 6. bring the total count of currently rented films per store
-- store --> inventory --> rental

select s.store_id, count(r.rental_id)
from sakila.store s
join sakila.inventory i on s.store_id = i.store_id
join sakila.rental r on i.inventory_id = r.inventory_id
where r.return_date IS NULL
group by s.store_id;

-- inventory --> rental
select i.store_id, count(r.rental_id)
from sakila.inventory i
join sakila.rental r on i.inventory_id = r.inventory_id
where r.return_date IS NULL
group by i.store_id;

-- 7. Using CTE customers with their respective rental details who made atleast 30 rentals
WITH rental_30 AS (
	select r.customer_id, count(*) as count
    from sakila.rental r
    group by r.customer_id
    having count(*) >= 30
)
select c.customer_id, c.first_name, c.last_name, r.count
from sakila.customer c
join rental_30 r on c.customer_id = r.customer_id;

use sakila;

-- 8. customers who rented same film twice or more than twice
-- customer --> rental --> inventory --> film
select c.customer_id, c.first_name, c.last_name, f.film_id, count(f.film_id)
from customer c
join rental r on c.customer_id = r.customer_id
join inventory i on r.inventory_id = i.inventory_id
join film f on i.film_id = f.film_id
group by c.customer_id, c.first_name, c.last_name, f.film_id
having count(f.film_id) >= 2
order by r.customer_id;

-- rental --> inventory --> film
select r.customer_id, f.film_id, count(f.film_id)
from rental r 
join inventory i on r.inventory_id = i.inventory_id
join film f on i.film_id = f.film_id
group by r.customer_id, f.film_id
having count(f.film_id) >= 2
order by r.customer_id, f.film_id;


-- 9. Using CTE find payments by customers in London City
-- customer --> payment --> address --> city

WITH city_london as (
	select c.city, p.*
    from city c
    join address a on a.city_id = c.city_id
    join customer cu on a.address_id = cu.address_id
    join payment p on cu.customer_id = p.customer_id
    where c.city = 'London'
)
select * from city_london;


-- 10. Using the sub-query, find customer who made greater than 8 payments
select *
from customer
where customer_id in
	(select customer_id 
		from payment
		group by customer_id
        having count(*) > 8);

























