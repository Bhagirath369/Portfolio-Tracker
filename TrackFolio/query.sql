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
	wacc numeric(10,2),
    sold_value numeric(10,2),
    realised_gain numeric(10,2)
);

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


CREATE OR REPLACE FUNCTION update_holding_table()
RETURNS TRIGGER AS
$$
DECLARE 
    stock_ltp NUMERIC;
    stock_percent_change NUMERIC;
    avg_wacc NUMERIC;
    sell_realized_gain NUMERIC;
BEGIN
    -- Fetch live stock data
    SELECT ltp, percent_change 
    INTO stock_ltp, stock_percent_change
    FROM live_stocks 
    WHERE stock_symbol = NEW.script;

    -- Ensure stock exists before SELL transaction
    IF NEW.transaction_type = 'SELL' AND NOT EXISTS (
        SELECT 1 FROM holding WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script
    ) THEN
        RAISE EXCEPTION 'Sell transaction is invalid! Stock does not exist in holdings';
    END IF;

    -- Check if stock exists in holding
    IF EXISTS (SELECT 1 FROM holding WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script) THEN
        -- Fetch the weighted average cost per unit
        SELECT wacc INTO avg_wacc
        FROM holding 
        WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script;

        -- Calculate the realized gain for sold stocks
        IF NEW.transaction_type = 'SELL' THEN
            sell_realized_gain := NEW.net_ammount - (NEW.quantity * avg_wacc);
        ELSE
            sell_realized_gain := 0;
        END IF;

        -- Update existing record
        UPDATE holding
        SET 
            total_quantity = 
                CASE 
                    WHEN NEW.transaction_type IN ('BUY', 'FPO', 'RIGHT', 'AUCTION', 'DIVIDENT', 'BONUS') THEN total_quantity + NEW.quantity
                    WHEN NEW.transaction_type IN ('SELL') THEN total_quantity - NEW.quantity
                    ELSE total_quantity
                END,
            total_investment =
                CASE 
                    WHEN NEW.transaction_type IN ('BUY', 'FPO', 'RIGHT', 'AUCTION', 'DIVIDENT', 'BONUS') THEN total_investment + NEW.net_ammount
                    WHEN NEW.transaction_type IN ('SELL') THEN total_investment -- total investment does not change on selling
                    ELSE total_investment
                END,
            sold_value = 
                CASE 
                    WHEN NEW.transaction_type IN ('SELL') THEN sold_value + NEW.net_ammount
                    ELSE sold_value
                END,
            realized_gain = realized_gain + sell_realized_gain,
            ltp = stock_ltp
        WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script;

        -- Update calculations
        UPDATE holding
        SET
            wacc = (total_investment / NULLIF(total_quantity, 0)),
            current_value = total_quantity * stock_ltp,
            today_profit_loss = current_value - total_investment, -- Assumed P&L calculation
            net_receivable_ammount = sold_value - total_investment
        WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script;

        -- Remove if quantity becomes zero
        IF EXISTS (SELECT 1 FROM holding WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script AND total_quantity = 0) THEN
            DELETE FROM holding WHERE portfolio_id = NEW.portfolio_id AND script = NEW.script;
        END IF;

    ELSE
        -- Insert new stock for valid transactions
        IF NEW.transaction_type IN ('IPO', 'BUY', 'FPO', 'RIGHT', 'AUCTION', 'DIVIDENT', 'BONUS') THEN
            INSERT INTO holding (portfolio_id, script, sector, total_quantity, total_investment, wacc, ltp, current_value, today_profit_loss, net_receivable_ammount, sold_value, realized_gain)
            VALUES (
                NEW.portfolio_id,
                NEW.script,
                NULL, -- Sector 
                NEW.quantity,
                NEW.net_ammount,
                NEW.net_ammount / NULLIF(NEW.quantity, 0),
                stock_ltp,
                NEW.quantity * stock_ltp,
                NULL, -- Cannot calculate today P&L initially
                NEW.quantity * stock_ltp,
                0,  -- Sold value initially 0
                0   -- Realized gain initially 0
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
    IF OLD.transaction_type IN ('IPO', 'BUY', 'FPO', 'RIGHT', 'AUCTION', 'DIVIDENT', 'BONUS') THEN
        UPDATE holding
        SET 
            total_quantity = total_quantity - OLD.quantity,
            total_investment = total_investment - (OLD.quantity * OLD.rate + COALESCE(OLD.comision, 0) + COALESCE(OLD.dp_charge, 0)),
            wacc = (total_investment / NULLIF(total_quantity, 0))
        WHERE portfolio_id = OLD.portfolio_id AND script = OLD.script;

    --If the deleted transaction was a SELL, just increase total_quantity
    ELSIF OLD.transaction_type = 'SELL' THEN
        UPDATE holding
        SET 
            wacc = (total_investment / NULLIF(total_quantity, 0)),
            total_quantity = total_quantity + OLD.quantity,
            sold_value = sold_value - OLD.quantity
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

--function to update portfolio table when holding is updated
CREATE OR REPLACE FUNCTION update_portfolio_table_after_add()
RETURNS TRIGGER AS 
$$
BEGIN
    -- Ensure portfolio exists
    IF EXISTS (SELECT 1 FROM portfolio WHERE portfolio_id = NEW.portfolio_id) THEN
    
        -- Update Portfolio Aggregates
        UPDATE portfolio
        SET
            total_investment = (SELECT COALESCE(SUM(total_investment), 0) FROM holding WHERE portfolio_id = NEW.portfolio_id),
            current_value = (SELECT COALESCE(SUM(current_value), 0) FROM holding WHERE portfolio_id = NEW.portfolio_id),
            today_gain_or_loss = (SELECT COALESCE(SUM(today_profit_loss), 0) FROM holding WHERE portfolio_id = NEW.portfolio_id),
            sold_value = (SELECT COALESCE(SUM(sold_value), 0) FROM holding WHERE portfolio_id = NEW.portfolio_id),
            realized_gain = (
                SELECT COALESCE(SUM(sold_value - (total_quantity * wacc)), 0)
                FROM holding
                WHERE portfolio_id = NEW.portfolio_id
            )
        WHERE portfolio_id = NEW.portfolio_id;
    
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER portfolio_after_insert
AFTER INSERT OR UPDATE OR DELETE ON holding
FOR EACH ROW
EXECUTE FUNCTION update_portfolio_table_after_add();


--function  to update portfolio table after deletion in holding
CREATE OR REPLACE FUNCTION update_portfolio_after_holding_delete()
RETURNS TRIGGER AS 
$$
BEGIN
    -- Ensure the portfolio exists before updating
    IF EXISTS (SELECT 1 FROM portfolio WHERE portfolio_id = OLD.portfolio_id) THEN
    
        -- Update Portfolio Aggregates After Holding is Deleted
        UPDATE portfolio
        SET
            total_investment = (SELECT COALESCE(SUM(total_investment), 0) FROM holding WHERE portfolio_id = OLD.portfolio_id),
            current_value = (SELECT COALESCE(SUM(current_value), 0) FROM holding WHERE portfolio_id = OLD.portfolio_id),
            today_gain_or_loss = (SELECT COALESCE(SUM(today_profit_loss), 0) FROM holding WHERE portfolio_id = OLD.portfolio_id)
        WHERE portfolio_id = OLD.portfolio_id;
    
    END IF;
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

--trigger to call update_portfolio_after_holding_delete()
CREATE TRIGGER portfolio_after_holding_delete
AFTER DELETE ON holding
FOR EACH ROW
EXECUTE FUNCTION update_portfolio_after_holding_delete();
