/* Drop tables if it already exists */
drop table if exists BROKER;
drop table if exists TRADER;

/* Create tables -- create a copy in home database */
create table BROKER (	
	contract_num int(11) not null,
	trader_id int(11) not null,
	trade_type varchar(11) not null,
	trading_symbol varchar(11) not null, 
	start_time datetime not null,
	due_time datetime not null,
	trade_price decimal(18,4) default null,
	trade_size int(11) default null,
	fee decimal(4,2) default null,
	net_profit decimal(18,4) default null,
	primary key(contract_num));

create table TRADER (
	trader_id int(11) not null,
	trader_name varchar(11) not null,
	balance decimal(50,2) default null,
	primary key(trader_id));

/* Populate tables */
insert BROKER values (0, 0, 'short', 'BHN', '2016-02-08 09:00:11', '2016-05-08 00:00:00', 66.0000, 8700, 0.02, null);
insert BROKER values (1, 1, 'short', 'BGA', '2016-02-18 09:20:42', '2016-05-18 00:00:00', 54.8490, 2600, 0.03, null);
insert BROKER values (2, 2, 'short', 'AEW', '2016-03-24 09:19:08', '2016-06-24 00:00:00', 74.8360, 900, 0.04, null);
insert BROKER values (3, 3, 'short', 'ARM', '2016-02-08 09:11:42', '2016-05-08 00:00:00', 96.0000, 3300, 0.01, null);
insert BROKER values (4, 4, 'short', 'AQO', '2016-03-18 09:16:50', '2016-06-18 00:00:00', 40.7750, 6800, 0.05, null);

insert TRADER values (0, 'peter', 100000);
insert TRADER values (1, 'anthony', 250000);
insert TRADER values (2, 'sarah', 115000);
insert TRADER values (3, 'john', 75000);
insert TRADER values (4, 'potter', 195000);
