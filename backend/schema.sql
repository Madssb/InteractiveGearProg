CREATE TABLE IF NOT EXISTS public.shares (
  token text PRIMARY KEY,
  sequence jsonb NOT NULL,
  items jsonb NOT NULL
);
