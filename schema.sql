	CREATE TABLE movements (
		id SERIAL PRIMARY KEY,
		lift TEXT
	);
	CREATE TABLE users(
		id SERIAL PRIMARY KEY,
		username TEXT UNIQUE,
		password TEXT
	);
	CREATE TABLE classes(
		id SERIAL PRIMARY KEY,
		max_weight INTEGER
		sport TEXT,
		open BOOL
	);
	CREATE TABLE results (
		id SERIAL PRIMARY KEY,
		user_id INTEGER REFERENCES users,
		movement_id INTEGER REFERENCES movements,
		weight DECIMAL(5,2),
		date DATE,
		class_id INTEGER REFERENCES classes,
		public BOOL,
		like_amount INTEGER DEFAULT 0,
		comp_id INTEGER DEFAULT 0
		
	);
	CREATE TABLE comments (
		id SERIAL PRIMARY KEY,
		comment TEXT,
		result_id INTEGER REFERENCES results
	);
	CREATE TABLE competition (
		id SERIAL PRIMARY KEY,
		name TEXT
	);
