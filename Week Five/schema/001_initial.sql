CREATE TABLE IF NOT EXISTS Project (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Task (
    id         INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    title      TEXT NOT NULL CHECK (length(title) BETWEEN 1 AND 200),
    status     TEXT NOT NULL DEFAULT 'todo'
               CHECK (status IN ('todo', 'in_progress', 'done')),
    due_date   TEXT,
    FOREIGN KEY (project_id) REFERENCES Project (id) ON DELETE RESTRICT
);
