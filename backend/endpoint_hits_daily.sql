CREATE TABLE IF NOT EXISTS public.endpoint_hits_daily (
  day date NOT NULL,
  endpoint text NOT NULL,
  hits bigint NOT NULL DEFAULT 0,
  PRIMARY KEY (day, endpoint)
);