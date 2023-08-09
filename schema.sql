	CREATE TABLE movements (
		id SERIAL PRIMARY KEY,
		lift TEXT
	);
	CREATE TABLE users(
		id SERIAL PRIMARY KEY,
		name TEXT,
		password TEXT
	);
	CREATE TABLE classes(
		id SERIAL PRIMARY KEY,
		max_weight INTEGER
	);
	CREATE TABLE results (
		id SERIAL PRIMARY KEY,
		user_id INTEGER REFERENCES users,
		movement_id INTEGER REFERENCES movements,
		weight DECIMAL(5,2),
		date DATE,
		class_id INTEGER REFERENCES classes
	);

