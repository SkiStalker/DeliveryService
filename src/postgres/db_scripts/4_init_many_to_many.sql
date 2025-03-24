CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

create table if not exists company.public.group_permission (
    group_id uuid not null,
    permission_id uuid not null,
    primary key (group_id, permission_id),
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW(),

    constraint fk_group foreign key (group_id) references company.public.group(id),
    constraint fk_permission foreign key (permission_id) references company.public.permission(id)
);



create table if not exists company.public.account_group (
    group_id uuid not null,
    account_id uuid not null,
    primary key (group_id, account_id),
    created_at timestamptz not null default NOW(),
    updated_at timestamptz not null default NOW(),

    constraint fk_group foreign key (group_id) references company.public.group(id),
    constraint fk_account foreign key (account_id) references company.public.account(id)
);