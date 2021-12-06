-- PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS 'User'('USER_ID'  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	'USERNAME' VARCHAR(20),
	'FNAME' VARCHAR(20), 
	'LNAME' VARCHAR(20),
	'PHONE' INTEGER(10),
	'CELL' INTEGER(10),
	'EMAIL' VARCHAR(50),
	'ROLE' VARCHAR(1) DEFAULT 'c',
	'HPWD' VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS 'Client'('CLIENT_ID' INTEGER,
	'MEMBERSHIP' VARCHAR(1) DEFAULT 's',
	'LIQUID_CASH' DECIMAL DEFAULT 0,
	'NO_OF_BITCOINS' INTEGER DEFAULT 0,
	PRIMARY KEY('CLIENT_ID'),
	FOREIGN KEY ('CLIENT_ID') REFERENCES 'User'('USER_ID') ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'Address'('CLIENT_ID'  INTEGER,
	'STREET' VARCHAR(20) NOT NULL,
	'CITY' VARCHAR(20) NOT NULL,
	'STATE' VARCHAR(20) NOT NULL,
	'ZIP' INTEGER(6) NOT NULL,
	FOREIGN KEY ('CLIENT_ID') REFERENCES 'Client' ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'Trader'('TRADER_ID' INTEGER,
	'LIQUID_CASH' DECIMAL,
	FOREIGN KEY ('TRADER_ID') REFERENCES 'User'('USER_ID') ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'WALLET_PAYMENT_TRANSACTIONS'('AMOUNT' INTEGER,
	'DATE_TIME' TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	'CLIENT_ID' INT
	-- FOREIGN KEY ('CLIENT_ID') REFERENCES 'Client' ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'MONEY_PAYMENT_TRANSACTIONS'('AMOUNT' INTEGER,
	'DATE_TIME' TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	'TRADER_ID' INT,
	'CLIENT_ID' INT,
	'FINAL_STATUS' VARCHAR(1),
	PRIMARY KEY ('CLIENT_ID', 'TRADER_ID', 'DATE_TIME')
	-- FOREIGN KEY ('CLIENT_ID') REFERENCES 'Client' ON DELETE CASCADE,
	-- FOREIGN KEY ('TRADER_ID') REFERENCES 'Trader' ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'BITCOIN_TRANSACTIONS'('NUMBER_OF_BITCOINS' DECIMAL,
	'PRICE' INTEGER,
	'DATE_TIME' TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	'COMMISSION_TYPE' VARCHAR(1),
	'COMMISSION_AMOUNT' INTEGER,
	'CLIENT_ID' INTEGER,
	'TRADER_ID' INTEGER DEFAULT NULL,
	'FINAL_STATUS' VARCHAR(1),
	PRIMARY KEY ('CLIENT_ID', 'DATE_TIME')
	-- PRIMARY KEY ('CLIENT_ID', 'TRADER_ID', 'DATE_TIME')
	-- FOREIGN KEY ('CLIENT_ID') REFERENCES 'Client' ON DELETE CASCADE,
	-- FOREIGN KEY ('TRADER_ID') REFERENCES 'Trader' ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'NET_AMOUNT'('NET_AMOUNT' INTEGER,
	'TRADER_ID' INT,
	'CLIENT_ID' INT,
	PRIMARY KEY ('CLIENT_ID', 'TRADER_ID')
	-- FOREIGN KEY ('CLIENT_ID') REFERENCES 'Client' ON DELETE CASCADE,
	-- FOREIGN KEY ('TRADER_ID') REFERENCES 'Trader' ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS 'REQUESTS'('AMOUNT' INTEGER,
	'DATE_TIME' TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	'NO_OF_BITCOINS' INTEGER NOT NULL,
	'TRADER_ID' INT,
	'CLIENT_ID' INT,
	'STATUS' VARCHAR(1),
	'COMMISION_TYPE' VARCHAR(10),
	PRIMARY KEY ('CLIENT_ID', 'TRADER_ID', 'DATE_TIME')
	-- FOREIGN KEY ('CLIENT_ID') REFERENCES 'Client' ON DELETE CASCADE,
	-- FOREIGN KEY ('TRADER_ID') REFERENCES 'Trader' ON DELETE CASCADE
);
