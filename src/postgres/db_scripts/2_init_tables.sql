CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

create table if not exists company.public.account (
    id uuid primary key default uuid_generate_v4(),
    username text not null UNIQUE,
    password text not null,
    first_name text not null,
    second_name text not null,
    patronymic text,
    birth timestamptz,
    email text,
    phone text,
    refresh_token text,
    is_active boolean not null default TRUE,
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

-----------------------------------------------------
-- TODO Move to MongoDB entity
-----------------------------------------------------
create table if not exists company.public.cargo (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    type text not null,
    description text not null,
    creator_id uuid not null,
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW(),
    constraint fk_creator foreign key (creator_id) references company.public.account(id)
);
-----------------------------------------------------


create table if not exists company.public.delivery (
    id uuid primary key default uuid_generate_v4(),

    state text not null,
    priority smallint not null,

    sender_id uuid not null,
    receiver_id uuid not null,
    cargo_id uuid not null,

    bill_id uuid,

    send_address_id uuid not null,
    receive_address_id uuid not null,

    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW(),

    constraint fk_sender foreign key (sender_id) references company.public.account(id),
    constraint fk_receiver foreign key (receiver_id) references company.public.account(id),

-----------------------------------------------------
-- TODO Move to MongoDB entity
-----------------------------------------------------
    constraint fk_cargo foreign key (cargo_id) references company.public.cargo(id),
-----------------------------------------------------

    constraint fk_send_address foreign key (send_address_id) references company.public.address(id),
    constraint fk_receive_address foreign key (receive_address_id) references company.public.address(id)
);


CREATE TABLE if not exists company.public.address (
    id uuid primary key default uuid_generate_v4(),
    country TEXT not null,
    region TEXT not null,
    city TEXT not null,
    street TEXT not null,
    house TEXT not null,
    apartment TEXT not null,
    postal_code TEXT not null
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW(),
);