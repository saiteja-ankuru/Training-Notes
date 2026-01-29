-- 1. Identify if there are duplicates in Customer table. Don't use customer id to check the duplicates 
SELECT first_name, last_name, email, COUNT(*) AS total_count
FROM sakila.customer
GROUP BY first_name, last_name, email
HAVING COUNT(*) > 1;


-- 2. Number of times letter 'a' is repeated in film descriptions 
SELECT
SUM(
  LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'a', ''))
) AS count_of_a
FROM sakila.film;


-- 3. Number of times each vowel is repeated in film descriptions 
SELECT
SUM(LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'a', ''))) AS count_of_a,
SUM(LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'e', ''))) AS count_of_e,
SUM(LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'i', ''))) AS count_of_i,
SUM(LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'o', ''))) AS count_of_o,
SUM(LENGTH(description) - LENGTH(REPLACE(LOWER(description), 'u', ''))) AS count_of_u
FROM sakila.film;


-- 4. Display the payments made by each customer 1. Month wise 2. Year wise 3. Week wise 
-- 1. MONTH WISE
SELECT customer_id,
       YEAR(payment_date) AS year,
       MONTH(payment_date) AS month,
       SUM(amount) AS total_amount
FROM sakila.payment
GROUP BY customer_id, year, month;

-- 2. YEAR WISE
SELECT customer_id,
       YEAR(payment_date) AS year,
       SUM(amount) AS total_amount
FROM sakila.payment
GROUP BY customer_id, year;

-- 3. WEEK WISE
SELECT customer_id,
       YEAR(payment_date) AS year,
       WEEK(payment_date) AS week,
       SUM(amount) AS total_amount
FROM sakila.payment
GROUP BY customer_id, year, week;


-- 5. Check if any given year is a leap year or not. You need not consider any table from sakila database. 
-- Write within the select query with hardcoded date 
SELECT
CASE
  WHEN (2024 % 400 = 0)
    OR (2024 % 4 = 0 AND 2024 % 100 <> 0)
  THEN 'Leap Year'
  ELSE 'Not a Leap Year'
END AS leap_year_status;

SELECT
CASE
  WHEN (2026 % 400 = 0)
    OR (2026 % 4 = 0 AND 2026 % 100 <> 0)
  THEN 'Leap Year'
  ELSE 'Not a Leap Year'
END AS leap_year_status;


-- 6. Display number of days remaining in the current year from today. 
SELECT
DATEDIFF(
  STR_TO_DATE(CONCAT(YEAR(CURDATE()), '-12-31'), '%Y-%m-%d'),
  CURDATE()
) AS days_remaining;


-- 7. Display quarter number(Q1,Q2,Q3,Q4) for the payment dates from payment table. 
SELECT payment_id,
       payment_date,
       CONCAT('Q', QUARTER(payment_date)) AS quarter
FROM sakila.payment;


-- 8. Display the age in year, months, days based on your date of birth. For example: 21 years, 4 months, 12 days
SELECT
CONCAT(
  TIMESTAMPDIFF(YEAR, '2002-12-28', CURDATE()), ' years, ',
  MOD(TIMESTAMPDIFF(MONTH, '2002-12-28', CURDATE()), 12), ' months, ',
  DATEDIFF(
    CURDATE(),
    DATE_ADD(
      '2002-12-28',
      INTERVAL TIMESTAMPDIFF(MONTH, '2002-12-28', CURDATE()) MONTH
    )
  ), ' days'
) AS age;
