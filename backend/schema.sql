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

CREATE TABLE IF NOT EXISTS public.annotations (
  annotation_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  message_id bigint UNIQUE,
  milestone_id integer NOT NULL,
  user_id bigint NOT NULL,
  up_count integer NOT NULL DEFAULT 0 CHECK (up_count >= 0),
  down_count integer NOT NULL DEFAULT 0 CHECK (down_count >= 0),
  chart_version text NOT NULL,
  annotation_text text NOT NULL,
  created_at date NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX IF NOT EXISTS annotations_milestone_chart_idx
  ON public.annotations (milestone_id, chart_version);

CREATE INDEX IF NOT EXISTS annotations_user_idx
  ON public.annotations (user_id);
