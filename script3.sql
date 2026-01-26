#strings
select title from sakila.film;

select title, lpad(rpad(title, 20, '*'), 25, '*') as left_padded
from sakila.film
limit 5;

select title, rpad(title, 20, '*') as right_padded
from sakila.film
limit 5;

# susstring
select title, substring(title, 3, 9) as short_title
from sakila.film;

#concatenation
select concat(first_name, '@', last_name) as full_name
from sakila.customer;

select title, reverse(title) as reversed_title
from sakila.film
limit 5;


#length
select title, length(title) as title_length
from sakila.film
where length(title) = 8;

#substring with locate
select email from sakila.customer;

select email, substring(email, locate('@', email) + 1) as domain
from sakila.customer;

select email, substring_index(substring(email, locate('@', email) + 1), '.', -1) as domain
from sakila.customer;

select email, substring_index(email, '@',-1) 
from sakila.customer;

select title, upper(title), lower(title)
from sakila.film
where upper(title) like '%LOVELY%' or upper(title) like '%MAN';

select title, lower(title) as lower_titles
from sakila.film;

select left(title, 1) as first_letter, right(title, 1) as last_letter, title, count(*) as film_count
from sakila.film
group by left(title, 1), right(title, 1)
order by film_count DESC;

select left(title, 2) as first_letter, right(title, 3) as last_letter, title
from sakila.film;

------------------------------
select last_name,
		case
			when left(last_name, 1) between 'A' and 'M' then 'Group A-M'
            when left(last_name, 1) between 'N' and 'Z' then 'Group N-Z'
            else 'other'
		end as group_label
from sakila.customer;


select title, replace(title, 'A', 'x') as cleaned_title
from sakila.film
where title like '% ' '%';

--------------------------------
-- not contains 3 consecutive vowels (^--> not)
select customer_id, last_name
from sakila.customer
where last_name REGEXP '[^aeiouAEIOU]{3}';

-- ends with vowel
select lower(title)
from sakila.film
where title REGEXP '[aeiouAEIOU]$';

select title, right(title,2)
from sakila.film
where title REGEXP '[eE]$';


-- count
select right(title, 1), count(*)
from sakila.film
where title REGEXP '[aeiouAEIOU]$'
group by right(title, 1);

select title as ending, right(title, 1)
from sakila.film
where title REGEXP '[Ee]$';


---------------------------------------------
-- match

select title, rental_rate, rental_rate^3 as double_rate
from sakila.film;

-- select amount, cast(amount as signed) as amount_str

select customer_id,
		count(payment_id) as payments,
        sum(amount) as total_paid,
        sum(amount)/count(payment_id) as avg_payment
from sakila.payment
Group by customer_id;

select rental_duration, cost_efficiency_dup1 from sakila.film;

select rental_duration from sakila.film;

ALTER TABLE sakila.film
ADD COLUMN cost_efficiency_dup1 DECIMAL(6,2);

SET SQL_SAFE_UPDATES = 0;


UPDATE sakila.film
set cost_efficiency_dup1 = rental_duration * 2
where length is not null;

select * from sakila.film;

select customer_id, (rand() * 100), floor(rand() * 100) as random_score
from sakila.customer
limit 5;

select film_id, rental_duration, power(rental_duration, 2) as squared_duration
from sakila.film
limit 5;

select film_id, length, mod(length, 60) as minute_over_hour
from sakila.film;

select rental_rate, floor(rental_rate) as floor_value, ceil(rental_rate) as ceil_value
from sakila.film;

select rental_rate, round(replacement_cost / rental_rate, 0), round(replacement_cost / rental_rate, 1) as ratio
from sakila.film;

select rental_id, return_date, rental_date, datediff(return_date, rental_date) as days_rented
from sakila.rental
where return_date is not null;

select last_update, yearweek(last_update), monthname(last_update) from sakila.film;

select rental_date, year(rental_date) from sakila.rental;

select payment_date from sakila.payment;

select payment_date, date(payment_date) as pay_date, sum(amount) as total_paid
 from sakila.payment
 group by payment_date, date(payment_date)
 order by pay_date desc;
 
 













