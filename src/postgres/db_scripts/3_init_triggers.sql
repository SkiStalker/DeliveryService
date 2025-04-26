CREATE TRIGGER trigger_set_timestamps_account
BEFORE INSERT OR UPDATE ON company.public.account
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps_permission
BEFORE INSERT OR UPDATE ON company.public.permission
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps_group
BEFORE INSERT OR UPDATE ON company.public.group
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();


CREATE TRIGGER trigger_set_timestamps_cargo
BEFORE INSERT OR UPDATE ON company.public.cargo
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps_delivery
BEFORE INSERT OR UPDATE ON company.public.delivery
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps_address
BEFORE INSERT OR UPDATE ON company.public.address
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();