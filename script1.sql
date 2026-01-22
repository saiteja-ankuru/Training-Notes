CREATE DATABASE company_db;

Create table company_db.test_table (
Id INT,
Name VARCHAR(100)
);

SELECT id from company_db.test_table;

INSERT INTO company_db.test_table (id, name)
VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Charlie');


#Select
SELECT * from company_db.test_table;

#Alter table
ALTER TABLE company_db.test_table
ADD Email varchar(255);

SELECT * from company_db.test_table;

ALTER TABLE company_db.test_table
RENAME COLUMN Email to email_id;

SELECT * from company_db.test_table;

Drop table if exists company_db.Persons;

CREATE TABLE company_db.Persons (
ID int NOT NULL unique,
LastName varchar(255) NOT NULL,
FirstName varchar(255),
Age int
);

Select * from company_db.Persons;

INSERT INTO company_db.Persons (ID, LastName, FirstName, Age)
VALUES (1, 'Smith', 'John', 30);
Select * from company_db.Persons;

INSERT INTO company_db.Persons (ID, LastName, FirstName, Age)
VALUES (2, 'Doe', NULL, NULL);
Select * from company_db.Persons;

INSERT INTO company_db.Persons (ID, LastName, FirstName, Age)
VALUES (1, 'Brown', 'Charlie', 25); -- this will fail, ID=1 already exists
Select * from company_db.Persons;

INSERT INTO company_db.Persons (ID, LastName, FirstName, Age)
VALUES (3, NULL, 'Alice', 28); -- lastname cannot be null
Select * from company_db.Persons;

# PRIMARY KEY
ALTER TABLE company_db.Persons
ADD PRIMARY KEY (ID);

SELECT CONSTRAINT_NAME
FROM information_schema.TABLE_CONSTRAINTS
Where TABLE_SCHEMA = 'company_db'
AND TABLE_NAME = 'Persons';

ALTER TABLE company_db.Persons
DROP PRIMARY KEY;

ALTER TABLE company_db.Persons
ADD CONSTRAINT  Pk_Person PRIMARY KEY (ID);

#Foreign Key – field in one table, refers to the primary key in another table
CREATE TABLE company_db.Orders (
OrderID INT PRIMARY KEY,
OrderDate DATE,
PersonID INT,
FOREIGN KEY (PersonID) REFERENCES Persons(ID)
ON DELETE RESTRICT
ON UPDATE CASCADE
);
-- CASCADE – if update primary key, value will update in child table
-- If delete in child table, throws error as value still referencing to parent table

INSERT INTO company_db.Orders (OrderID, OrderDate, PersonID)
VALUES (1001, ‘2024-06-10’, 1);

Select * from company_db.Orders;
Select * from company_db.Persons;

INSERT INTO company_db.Orders (OrderID, OrderDate, PersonID)
VALUES (1002, ‘2024-06-11’, 999); -- 999 DOESN’T EXIST

DELETE from company_db.Persons where ID=1;

Select * from company_db.Orders; -- child table
Select * from company_db.Persons; -- parent table

UPDATE from company_db.Persons SET ID=4 where ID=1;

CREATE TABLE company_db.Employee (
ID int NOT NULL,
LastName varchar(255) NOT NULL,
FirstName varchar(255),
Age int CHECK (Age>=18),
City varchar(255) DEFAULT ‘new york’
);

Select * from company_db. Employee;

INSET INTO company_db. Employee (ID, LastName, FirstName, Age, City)
VALUES (4, ‘joey’, ‘tribani, 22, ‘texas’)

INSET INTO company_db. Employee (ID, LastName, FirstName, Age)
VALUES (5, ‘joey’, ‘max’, 22) – default new York is added to city column

INSET INTO company_db. Employee (ID, LastName, FirstName, Age)
VALUES (2, ‘joey’, ‘max’, 17) –age constraint violated

