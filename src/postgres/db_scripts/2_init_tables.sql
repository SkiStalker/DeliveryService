CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

create table if not exists company.public.account (
    id uuid primary key default uuid_generate_v4(),
    username text not null,
    password text not null,
    first_name text,
    second_name text,
    patronymic text,
    birth timestamptz,
    email text,
    phone text,
    refresh_token text,
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW()
);


create table if not exists company.public.permission (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    description text not null,
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW()
);


create table if not exists company.public.group (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    description text not null,
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW()
);


create table if not exists company.public.cargo (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    type text not null,
    description text not null,
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW()
);


create table if not exists company.public.delivery (
    id uuid primary key default uuid_generate_v4(),

    state text not null,
    priority smallint not null,

    sender_id uuid not null,
    receiver_id uuid not null,
    cargo_id uuid not null,


    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW(),

    constraint fk_sender foreign key (sender_id) references company.public.account(id),
    constraint fk_receiver foreign key (receiver_id) references company.public.account(id),
    constraint fk_cargo foreign key (cargo_id) references company.public.cargo(id)
);
