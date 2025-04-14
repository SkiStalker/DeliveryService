CREATE INDEX idx_account_first_name_last_name ON company.public.account(first_name, second_name);

CREATE INDEX idx_cargo_creator_id ON company.public.cargo(creator_id);

CREATE INDEX idx_delivery_sender_id ON company.public.delivery(sender_id);
CREATE INDEX idx_delivery_receiver_id ON company.public.delivery(receiver_id);
CREATE INDEX idx_delivery_cargo_id ON company.public.delivery(cargo_id);
