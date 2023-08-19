	CREATE TABLE movements (
		id SERIAL PRIMARY KEY,
		lift TEXT
	);
	CREATE TABLE classes(
		id SERIAL PRIMARY KEY,
		max_weight INTEGER,
		sport TEXT,
		division CHAR
	);
	CREATE TABLE users(
		id SERIAL PRIMARY KEY,
		username TEXT UNIQUE,
		password TEXT,
		wl_class_id INTEGER REFERENCES classes(id),
		pl_class_id INTEGER REFERENCES classes(id),
		admin BOOL
	);
	CREATE TABLE results (
		id SERIAL PRIMARY KEY,
		user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
		movement_id INTEGER REFERENCES movements(id),
		weight DECIMAL(5,2),
		date DATE,
		public BOOL,
		like_amount INTEGER DEFAULT 0,
		comp_id INTEGER DEFAULT 0
	);
	CREATE TABLE comments (
		id SERIAL PRIMARY KEY,
		comment TEXT,
		result_id INTEGER REFERENCES results(id) ON DELETE CASCADE
	);
	CREATE TABLE competition (
		id SERIAL PRIMARY KEY,
		name TEXT
	);
