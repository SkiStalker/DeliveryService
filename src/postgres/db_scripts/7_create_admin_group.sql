WITH inserted_group AS (
    INSERT INTO company.public.group (name, description) VALUES
    ('Admin', 'Администраторы')
    RETURNING id
)

INSERT INTO company.public.group_permission (group_id, permission_id)
SELECT inserted_group.id, permission.id
FROM inserted_group, company.public.permission;