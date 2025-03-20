create table if not exists company.public.account (
    id int,
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW()
);