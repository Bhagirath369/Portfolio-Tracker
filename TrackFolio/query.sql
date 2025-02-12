create table users(
	id serial primary key,
	name varchar(150) not null,
	email varchar(255) not null,
	password varchar(255) not null
);

create table portfolio (
	portfolio_id serial primary key,
	user_id int,
	foreign key (user_id )references users(id),
	name varchar(255) not null,
	total_investment numeric(50,2),
	current_value numeric(50,2),
	sold_value numeric(50,2),
	realised_gain numeric(50,2),
	estimated_loss numeric(50,2),
	today_gain_or_loss numeric(50,2),
	type varchar(15) not null
);

CREATE TABLE transaction(
	transaction_id SERIAL PRIMARY KEY,
	portfolio_id INT,
	FOREIGN KEY(portfolio_id) REFERENCES portfolio(portfolio_id),
	transaction_date DATE,
	script varchar(20) NOT NULL,
	transaction_type varchar(5),
	quantity int check (quantity > 0),
	rate numeric(50,2) check(rate > 0),
	comision numeric(50,2),
	dp_charge int,
	net_ammount numeric(100,2),
	cps numeric(50,2)
);

create table holding (
    stock_id serial primary key,
	portfolio_id int, 
	foreign key(portfolio_id) references portfolio(portfolio_id),
    script varchar(20) unique,
    sector varchar(20),
    total_quantity int,
    total_investment numeric(50,2),
    ltp numeric(10,2),
    current_value numeric(50,2),
    today_profit_loss numeric(50,2),
    net_receivable_ammount numeric(50,2),
	wacc numeric(10,2)
);

--function to update holding table on addition of transaction
CREATE OR REPLACE FUNCTION update_holding_table()
RETURNS TRIGGER AS
$$
BEGIN
    -- Check if the stock already exists in the holding table
    IF EXISTS (SELECT 1 FROM holding WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script) THEN
        -- Update the existing holding record based on transaction type
        UPDATE holding
        SET 
            total_quantity = total_quantity + 
                CASE 
                    WHEN NEW.transaction_type IN ('BUY', 'FPO', 'RIGHT', 'AUCTION', 'DIVIDENT') THEN NEW.quantity
                    WHEN NEW.transaction_type = 'BONUS' THEN NEW.quantity -- Bonus shares add quantity with rate = 0
                    WHEN NEW.transaction_type = 'SELL' THEN -NEW.quantity
                    ELSE 0
                END,
            total_investment = total_investment + 
                CASE 
                    WHEN NEW.transaction_type IN ('BUY', 'FPO', 'RIGHT', 'AUCTION') THEN (NEW.quantity * NEW.rate + COALESCE(NEW.comision, 0) + COALESCE(NEW.dp_charge, 0))
                    WHEN NEW.transaction_type = 'BONUS' THEN 0 -- Bonus shares do not affect investment
                    WHEN NEW.transaction_type = 'SELL' THEN 0 -- Selling should not increase total investment
                    ELSE 0
                END
        WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script;
		--to update wacc
		UPDATE holding
		SET
			wacc = (total_investment / NULLIF(total_quantity, 0))
		WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script;
        -- Remove stock if total_quantity becomes zero
        DELETE FROM holding WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script AND total_quantity = 0;

    ELSE
        -- Insert a new record if script does not exist and transaction type is IPO
        IF NEW.transaction_type IN ('IPO' ,'BUY', 'AUCTION')THEN
            INSERT INTO holding (portfolio_id, script, sector, total_quantity, total_investment, wacc)
            VALUES (
                NEW.portfolio_id,
                NEW.script,
                NULL, -- Sector should be assigned manually or dynamically fetched
                NEW.quantity,
                (NEW.quantity * NEW.rate + COALESCE(NEW.comision, 0) + COALESCE(NEW.dp_charge, 0)),
                (NEW.quantity * NEW.rate + COALESCE(NEW.comision, 0) + COALESCE(NEW.dp_charge, 0)) / NEW.quantity
            );
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



--trigger to update holding table on addition of transaction
create trigger trg_to_update_holding 
after insert on transaction
for each row execute function update_holding_table()

--funcition to update holding table on deletion of transaction
CREATE OR REPLACE FUNCTION recalculate_holding_after_delete()
RETURNS TRIGGER AS
$$
BEGIN
    -- If the deleted transaction was a BUY/FPO/RIGHT/AUCTION, subtract its quantity and investment
    IF OLD.transaction_type IN ('BUY', 'FPO', 'RIGHT', 'AUCTION', 'DIVIDENT') THEN
        UPDATE holding
        SET 
            total_quantity = total_quantity - OLD.quantity,
            total_investment = total_investment - (OLD.quantity * OLD.rate + COALESCE(OLD.comision, 0) + COALESCE(OLD.dp_charge, 0)),
            wacc = (total_investment / NULLIF(total_quantity, 0))
        WHERE portfolio_id = OLD.portfolio_id AND script = OLD.script;

    -- If the deleted transaction was a SELL, just increase total_quantity
    ELSIF OLD.transaction_type = 'SELL' THEN
        UPDATE holding
        SET 
            total_quantity = total_quantity + OLD.quantity
        WHERE portfolio_id = OLD.portfolio_id AND script = OLD.script;
    END IF;

    -- Remove stock if total_quantity becomes zero
    DELETE FROM holding WHERE portfolio_id = OLD.portfolio_id AND script = OLD.script AND total_quantity = 0;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

--trigger to update holding table on deletion of tranasdaction
CREATE TRIGGER transaction_after_delete
AFTER DELETE ON transaction
FOR EACH ROW
EXECUTE FUNCTION recalculate_holding_after_delete();

-- table for live_stocks data in db
CREATE TABLE live_stocks (
    id SERIAL PRIMARY KEY,
    stock_symbol VARCHAR(10) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    ltp NUMERIC,
    percent_change NUMERIC,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC
);

