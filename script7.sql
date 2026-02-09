-- STORED PROCEDURES
-- ##################################

DROP PROCEDURE IF EXISTS sakila.GetCustomerPayments;
DELIMITER //

-- IN parameter only
CREATE PROCEDURE sakila.GetCustomerPayments(IN cid INT)
BEGIN
    SELECT payment_id, amount, payment_date
    FROM sakila.payment
    WHERE customer_id = cid;
END;
//


DROP PROCEDURE IF EXISTS sakila.TotalPaid;

//
-- OUT parameter
CREATE PROCEDURE sakila.TotalPaid(IN cid INT, OUT total DECIMAL(10,2))
BEGIN
    SELECT SUM(amount) INTO total
    FROM sakila.payment
    WHERE customer_id = cid ;
END;
//

DROP PROCEDURE IF EXISTS sakila.DynamicQuery;
//
-- Dynamic SQL procedure
CREATE PROCEDURE sakila.DynamicQuery(IN tbl_name VARCHAR(64))
BEGIN
    SET @s = CONCAT('SELECT COUNT(*) AS total_rows FROM ', tbl_name);
    PREPARE stmt FROM @s;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END;
//


DELIMITER ;

-- CALL examples:

CALL sakila.GetCustomerPayments(7);
-------------------------------------------
-- SET @rents = 0; CALL sakila.IncrementRentals(3, @rents); SELECT @rents;
------------------------------------------------------------------------------------------

CALL sakila.TotalPaid(6, @total); SELECT @total;

-------------------------------------------------------------

CALL sakila.DynamicQuery('sakila.customer');

-----------------------------------------------------
CALL sakila.TotalPaid(7, @total); 

SELECT @total;


-- Stored Procedure
-- ##################################

-- Create a temp table to store SELECT statements
DROP TEMPORARY TABLE IF EXISTS sakila.select_statements; 

CREATE TEMPORARY TABLE sakila.select_statements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    statement_text TEXT
);

-- drop PROCEDURE sakila.StoreSelectStatements;
-- Create the procedure
DELIMITER //

CREATE PROCEDURE sakila.StoreSelectStatements(IN db_name VARCHAR(64))
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE tbl_name VARCHAR(64);
    DECLARE cur CURSOR FOR
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = db_name;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO tbl_name;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET @stmt = CONCAT('SELECT count(*) FROM ', db_name, '.', tbl_name, ';');
        SET @ins = CONCAT('INSERT INTO select_statements (statement_text) VALUES (?)');
        PREPARE stmt FROM @ins;
        EXECUTE stmt USING @stmt;
        DEALLOCATE PREPARE stmt;

    END LOOP;

    CLOSE cur;
END;
//

DELIMITER ;

-- Call the procedure
CALL sakila.StoreSelectStatements('sakila');

-- See results
SELECT * FROM sakila.select_statements;