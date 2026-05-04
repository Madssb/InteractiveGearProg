CREATE TABLE IF NOT EXISTS public.shares (
  token text PRIMARY KEY,
  milestone_sequence jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS public.endpoint_hits (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  endpoint text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.milestones_completed_snapshots (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  milestones_completed jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.milestones_hidden_snapshots (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  milestones_hidden jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
