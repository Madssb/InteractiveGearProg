CREATE TABLE milestones_completed_snapshots (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    milestones_completed jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);