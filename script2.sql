Select * from sakila.actor;

Select distinct(first_name) from sakila.actor;

Select * from sakila.film where original_language_id is null;

Select count(*) from sakila.film;

Select distinct title from sakila.film where original_language_id is null;

Select count(distinct (title)) from sakila.film;

Select count(first_name) from sakila.actor;

Select count(distinct (first_name)) from sakila.film;
# select specific columns
Select first_name, last_name from sakila.actor;

#limit
Select first_name, last_name from sakila.actor limit 5;

#filtering with WHERE
Select distinct(rating) from sakila.film;

Select distinct(rating) from sakila.film where rating = 'R' and length >=92;

Select distinct(rating) from sakila.film where length >=92;

#sorting
Select rental_rate from sakila.film;

Select rental_rate from sakila.film order by rental_rate desc;

#AND #OR Operators
Select * from sakila.film
where rating = 'PG' and rental_duration =5
order by rental_rate ASC;

Select * from sakila.film
where rating = 'PG' or rental_duration =5
order by rental_rate ASC;

#NOT
Select * from sakila.film
where rental_duration NOT IN (6,7,3)
order by rental_rate ASC;

Select * from sakila.film
where NOT rental_duration = 6
order by rental_rate ASC;

Select * from sakila.film
where rental_duration = 6 and (rating = 'G' or rating = 'PG')
order by rental_rate ASC;

#LIKE used with where clause

Select * from sakila.city where city like 'A%s';

Select * from sakila.city where city like '_s__-d%';

#NULL value
#check rentals that were never returned

Select * from sakila.rental;

Select rental_id, inventory_id, customer_id, rental_date
from sakila.rental 
where rental_date IS NULL;

#between
Select rental_id, inventory_id, customer_id, rental_date
from sakila.rental 
where rental_date between ‘2005-05-26’ and ‘2005-05-30’;

#group by and having
#to check duplicates

Select customer_id, count(*) as count
From sakila.rental
Group by customer_id
Having count(*) <= 30
Order by count desc;


Select * from sakila.rental where return_date IS NULL;

Select * from sakila.rental where customer_id=33;

Select * from sakila.payment;

Select cutomer_id, sum(amount) as total_amount
From sakila.payment
Group by customer_id
Having sum(amount) > 100 and customer_id between 1 and 100;

