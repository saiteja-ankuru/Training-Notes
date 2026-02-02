# Joins
# Inner Join

select f.title, l.name as Language
from sakila.film f
inner join sakila.language l on f.language_id = l.language_id;


# left join
select f.title, c.name as category
from sakila.film f
left join sakila.film_category fc on f.film_id=fc.film_id
left join sakila.category c on fc.category_id = c.category_id;

select c.customer_id, c.first_name, r.rental_id
from sakila.customer c
inner join sakila.rental r on c.customer_id = r.customer_id;


# full outer join
## there is no full outer join directly in MySQL, so union of left and right joins gives full outer join
select a.actor_id, a.first_name, fa.film_id
from sakila.actor a
left join sakila.film_actor fa on a.actor_id = fa.actor_id
union
select a.actor_id, a.first_name, fa.film_id
from sakila.actor a
right join sakila.film_actor fa on a.actor_id = fa.actor_id;


select c.customer_id, r.rental_id
from sakila.customer
left join sakila.rental r on c.customer_id = r.customer_id
union
select c.customer_id, r.rental_id
from sakila.customer
right join sakila.rental r on c.customer_id = r.customer_id;


#self join
select s1.staff_id, s2.staff_id, s1.store_id
from sakila.staff s1
join sakila.staff s2 on s1.store_id = s2.store_id
where s1.staff_id = s2.staff_id;





