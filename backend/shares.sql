CREATE TABLE IF NOT EXISTS public.shares (
  token text PRIMARY KEY,
  milestone_sequence jsonb NOT NULL
);