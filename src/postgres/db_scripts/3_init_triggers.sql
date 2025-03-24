CREATE TRIGGER trigger_set_timestamps
BEFORE INSERT OR UPDATE ON company.public.account
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps
BEFORE INSERT OR UPDATE ON company.public.permission
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps
BEFORE INSERT OR UPDATE ON company.public.group
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps
BEFORE INSERT OR UPDATE ON company.public.cargo
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();

CREATE TRIGGER trigger_set_timestamps
BEFORE INSERT OR UPDATE ON company.public.delivery
FOR EACH ROW
EXECUTE FUNCTION set_timestamps();