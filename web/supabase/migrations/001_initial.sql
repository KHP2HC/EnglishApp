-- EnglishCoach Pro — Initial Schema Migration
-- Run in Supabase SQL Editor or via `supabase db push`

-- ── PROFILES ──────────────────────────────────────────────────────────
create table if not exists profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  name         text not null default '',
  avatar_emoji text default '🧑',
  target_exam  text check (target_exam in ('TOEIC','IELTS','TOEFL','VSTEP')),
  target_score numeric(4,1),
  current_band numeric(3,1),
  skill_bands  jsonb default '{}'::jsonb,
  exam_date    date,
  free_time    jsonb default '{"mon":60,"tue":60,"wed":60,"thu":60,"fri":60,"sat":120,"sun":120}'::jsonb,
  session_time text check (session_time in ('MORNING','AFTERNOON','EVENING')) default 'MORNING',
  streak_days  int default 0,
  total_xp     int default 0,
  last_active  date,
  onboarded    boolean default false,
  created_at   timestamptz default now()
);
alter table profiles enable row level security;
create policy "own profile" on profiles using (auth.uid() = id);

-- ── VOCABULARY CARDS (shared seed data) ──────────────────────────────
create table if not exists vocab_cards (
  id               uuid primary key default gen_random_uuid(),
  word             text not null,
  phonetic         text,
  meaning_en       text not null,
  meaning_vi       text not null,
  example_sentence text,
  audio_url        text,
  exam_type        text[] default '{}',
  cefr_level       text check (cefr_level in ('A1','A2','B1','B2','C1','C2')),
  category         text default 'general',
  created_at       timestamptz default now()
);

-- ── USER VOCABULARY PROGRESS (SRS) ───────────────────────────────────
create table if not exists vocab_progress (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid references profiles(id) on delete cascade,
  card_id        uuid references vocab_cards(id),
  interval_days  int default 1,
  easiness       numeric(3,2) default 2.5,
  repetitions    int default 0,
  next_review    date default current_date,
  last_quality   int,
  times_seen     int default 0,
  times_correct  int default 0,
  unique (user_id, card_id)
);
alter table vocab_progress enable row level security;
create policy "own progress" on vocab_progress using (auth.uid() = user_id);

-- ── STUDY SESSIONS ───────────────────────────────────────────────────
create table if not exists study_sessions (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references profiles(id) on delete cascade,
  started_at   timestamptz default now(),
  ended_at     timestamptz,
  session_type text check (session_type in
                ('VOCABULARY','GRAMMAR','LISTENING','READING','WRITING','SPEAKING','MOCK')),
  xp_earned    int default 0,
  items_total  int default 0,
  items_correct int default 0
);
alter table study_sessions enable row level security;
create policy "own sessions" on study_sessions using (auth.uid() = user_id);

-- ── ERROR JOURNAL ────────────────────────────────────────────────────
create table if not exists error_journal (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid references profiles(id) on delete cascade,
  session_id       uuid references study_sessions(id),
  error_category   text,
  skill            text,
  question_snapshot text,
  user_answer      text,
  correct_answer   text,
  created_at       timestamptz default now()
);
alter table error_journal enable row level security;
create policy "own errors" on error_journal using (auth.uid() = user_id);

-- ── STUDY PLANS ──────────────────────────────────────────────────────
create table if not exists study_plans (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references profiles(id) on delete cascade,
  week_start  date not null,
  daily_tasks jsonb not null default '{}'::jsonb,
  created_at  timestamptz default now(),
  unique (user_id, week_start)
);
alter table study_plans enable row level security;
create policy "own plans" on study_plans using (auth.uid() = user_id);

-- ── CONTENT CACHE ────────────────────────────────────────────────────
create table if not exists content_cache (
  id             uuid primary key default gen_random_uuid(),
  content_type   text,
  source_url     text,
  title          text,
  body           text,
  cefr_level     text,
  exam_type      text,
  fetched_at     timestamptz default now(),
  expires_at     timestamptz default now() + interval '7 days'
);

-- ── WRITING SUBMISSIONS ──────────────────────────────────────────────
create table if not exists writing_submissions (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references profiles(id) on delete cascade,
  task_prompt  text,
  user_essay   text,
  ai_feedback  jsonb,
  band_estimate numeric(3,1),
  created_at   timestamptz default now()
);
alter table writing_submissions enable row level security;
create policy "own submissions" on writing_submissions using (auth.uid() = user_id);

-- ── AUTO-CREATE PROFILE ON SIGNUP ───────────────────────────────────
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into profiles (id, name)
  values (new.id, split_part(new.email, '@', 1));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();

-- ── UPDATED_AT TRIGGER HELPER ────────────────────────────────────────
create or replace function update_updated_at()
returns trigger language plpgsql as $$
begin
  new.last_active = current_date;
  return new;
end;
$$;
