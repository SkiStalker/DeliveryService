create or replace function set_timestamps()
returns trigger as $$
begin
    IF TG_OP = 'INSERT' THEN
        NEW.created_at := NOW();
        NEW.updated_at := NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at := NOW();
    END IF;
    RETURN NEW;
end;
$$ language plpgsql;

create or replace function update_related_timestamps(target_table text, target_column text, old_id uuid, new_id uuid)
returns void as $$
begin
    EXECUTE format(
        'UPDATE company.public.%I SET updated_at = NOW() WHERE %I = $1 OR %I = $2',
        target_table, target_column, target_column
    ) USING old_id, new_id;
end;
$$ language plpgsql;



create or replace function group_permission_trigger_update_related_timestamps()
returns trigger as $$
begin
    perform update_related_timestamps('permission', 'id', OLD.permission_id, NEW.permission_id);
    perform update_related_timestamps('group', 'id', OLD.group_id, NEW.group_id);
    
    IF TG_OP = 'INSERT' THEN
        NEW.created_at := NOW();
        NEW.updated_at := NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at := NOW();
    END IF;
    return new;
end;
$$ language plpgsql;

create or replace function account_group_trigger_update_related_timestamps()
returns trigger as $$
begin
    perform update_related_timestamps('account', 'id', OLD.account_id, NEW.account_id);
    perform update_related_timestamps('group', 'id', OLD.group_id, NEW.group_id);

    IF TG_OP = 'INSERT' THEN
        NEW.created_at := NOW();
        NEW.updated_at := NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at := NOW();
    END IF;
    return new;
end;
$$ language plpgsql;