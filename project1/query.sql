CREATE DATABASE sales_hub;
USE sales_hub;
CREATE TABLE branches (
    branch_id INT PRIMARY KEY,
    branch_name VARCHAR(100),
    branch_admin_name VARCHAR(100)
);
CREATE TABLE customer_sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,        -- Unique ID for each sale
    branch_id INT NOT NULL,                        -- Reference to branch
    date DATE NOT NULL,                            -- Sale date
    name VARCHAR(100) NOT NULL,                    -- Customer name
    mobile_number VARCHAR(15) NOT NULL,            -- Customer mobile
    product_name VARCHAR(30) NOT NULL,            -- Product sold (DS/DA/BA/FSD)
    gross_sales DECIMAL(12,2) NOT NULL,           -- Total sale amount
    received_amount DECIMAL(12,2) DEFAULT 0,      -- Amount received (updated via triggers)
    pending_amount DECIMAL(12,2) 
        GENERATED ALWAYS AS (gross_sales - received_amount) STORED,  -- Auto-calculated
    status ENUM('Open','Close') DEFAULT 'Open',   -- Sale completion status
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)   -- Relational integrity
);
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,              -- Unique ID for each user
    username VARCHAR(100) NOT NULL,                      -- Admin username
    password VARCHAR(255) NOT NULL,                      -- User password (hashed recommended)
    branch_id INT,                                       -- Assigned branch
    role ENUM('Super Admin', 'Admin') NOT NULL,         -- User role
    email VARCHAR(255) UNIQUE NOT NULL,                 -- Unique email ID
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)  -- Links to branches table
);
CREATE TABLE payment_splits (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,          -- Unique ID for each payment
    sale_id INT NOT NULL,                               -- Reference to customer_sales
    payment_date DATE NOT NULL,                         -- Payment date
    amount_paid DECIMAL(12,2) NOT NULL,                -- Amount paid in this transaction
    payment_method VARCHAR(50) NOT NULL,               -- Cash / UPI / Card
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
);
SHOW VARIABLES LIKE 'secure_file_priv';


LOAD DATA LOCAL INFILE 'D:/guvi/project1/csv files/branches.csv'
INTO TABLE branches
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SHOW VARIABLES LIKE 'local_infile';
SET GLOBAL local_infile = 1;


LOAD DATA LOCAL INFILE 'D:/guvi/project1/csv files/customer_sales.csv'
REPLACE INTO TABLE customer_sales
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@date)
SET date = STR_TO_DATE(@date,'%d-%m-%Y');

DESCRIBE customer_sales;

LOAD DATA LOCAL INFILE 'D:/guvi/project1/csv files/customer_sales.csv'
INTO TABLE customer_sales
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'D:/guvi/project1/csv files/payment_splits.csv'
INTO TABLE payment_splits
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'D:/guvi/project1/csv files/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

DELIMITER $$

CREATE TRIGGER update_received_amount
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN

UPDATE customer_sales
SET received_amount =
(
    SELECT SUM(amount_paid)
    FROM payment_splits
    WHERE sale_id = NEW.sale_id
)
WHERE sale_id = NEW.sale_id;

END$$

DELIMITER ;