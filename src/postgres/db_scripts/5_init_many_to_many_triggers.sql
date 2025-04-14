CREATE TRIGGER trigger_set_timestamps_group_permission
BEFORE INSERT OR UPDATE OR DELETE ON company.public.group_permission
FOR EACH ROW
EXECUTE FUNCTION group_permission_trigger_update_related_timestamps();

CREATE TRIGGER trigger_set_timestamps_account_group
BEFORE INSERT OR UPDATE OR DELETE ON company.public.account_group
FOR EACH ROW
EXECUTE FUNCTION account_group_trigger_update_related_timestamps();