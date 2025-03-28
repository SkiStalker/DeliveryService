WITH inserted_user AS (
    INSERT INTO company.public.account 
    (username, password, first_name, second_name) 
    VALUES 
    ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin', 'Administratorov')
    RETURNING id
),
inserted_group AS (
    SELECT id
    FROM company.public.group
    WHERE name = 'Admin'
    LIMIT 1
)
INSERT INTO company.public.account_group (account_id, group_id)
SELECT inserted_user.id, inserted_group.id
FROM inserted_user, inserted_group;