CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contest TEXT,
  year INTEGER,
  paper TEXT,
  problem_no TEXT,
  stem TEXT,
  options_json TEXT,
  answer TEXT,
  solution TEXT,
  difficulty INTEGER,
  source TEXT,
  has_solution INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS question_tags (
  question_id INTEGER,
  tag_id INTEGER,
  PRIMARY KEY (question_id, tag_id)
);

CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id INTEGER,
  user_choice TEXT,
  is_correct INTEGER,
  elapsed_sec INTEGER,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  mode TEXT
);

CREATE TABLE IF NOT EXISTS mastery (
  tag_id INTEGER PRIMARY KEY,
  score REAL DEFAULT 0,
  attempts INTEGER DEFAULT 0,
  correct INTEGER DEFAULT 0,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_failures (
  row_number INTEGER,
  payload TEXT,
  error TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
