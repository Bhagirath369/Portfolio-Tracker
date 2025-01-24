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
    transaction_id int,
    foreign key(transaction_id) references transaction(transaction_id),
    script varchar(20),
    sector varchar(20),
    total_quantity int,
    total_investment numeric(50,2),
    ltp numeric(10,2),
    current_value numeric(50,2),
    today_profit_loss numeric(50,2),
    net_receivable_ammount numeric(50,2)
);
