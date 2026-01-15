-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Key-Value Store Table (for messages, reports, etc.)
create table public.kv_store (
  key text primary key,
  value text not null
);

-- Users Table
create table public.users (
  id text primary key,
  email text unique not null,
  password text not null,
  phone text,
  nric text,
  profile_data jsonb default '{}'::jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Matches Table
create table public.matches (
  user_id text references public.users(id),
  match_id text references public.users(id),
  timestamp timestamp with time zone default timezone('utc'::text, now()) not null,
  primary key (user_id, match_id)
);

-- Stories Table
create table public.stories (
  id text primary key,
  author_id text references public.users(id),
  content text not null,
  timestamp timestamp with time zone default timezone('utc'::text, now()) not null,
  likes integer default 0,
  badges text -- Stored as comma-separated string or could be jsonb
);

-- Enable Row Level Security (RLS) - Optional for now but good practice
alter table public.kv_store enable row level security;
alter table public.users enable row level security;
alter table public.matches enable row level security;
alter table public.stories enable row level security;

-- KV Store Policies
create policy "KV store is accessible by everyone" on public.kv_store for all using (true);

-- Policies (Open for Demo Purpose - NOT SECURE FOR PRODUCTION)
create policy "Public profiles are viewable by everyone" on public.users for select using (true);
create policy "Users can insert their own profile" on public.users for insert with check (true);
create policy "Users can update own profile" on public.users for update using (true);

create policy "Matches are viewable by everyone" on public.matches for select using (true);
create policy "Users can insert matches" on public.matches for insert with check (true);

create policy "Stories are viewable by everyone" on public.stories for select using (true);
create policy "Users can insert stories" on public.stories for insert with check (true);
create policy "Users can update stories" on public.stories for update using (true);
