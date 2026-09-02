CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  technology TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'planned',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
