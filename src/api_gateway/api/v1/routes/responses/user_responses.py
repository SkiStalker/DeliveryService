from api.v1.routes.responses.responses_parts.server_responses_parts import (
    internal_error_response,
)
from api.v1.routes.responses.responses_parts.account_responses_parts import (
    check_permission_error_response,
    check_permission_failed_response,
)
from api.v1.routes.responses.responses_parts.user_responses_parts import (
    user_already_exists_response,
    user_created_response,
    user_not_found_response,
)


get_users_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
}

get_user_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **user_not_found_response,
}

update_user_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **user_not_found_response,
    **user_already_exists_response,
}

delete_user_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **user_not_found_response,
}

reactivate_user_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **user_not_found_response,
}

create_user_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **user_already_exists_response,
    **user_created_response,
}


find_user_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **user_not_found_response,
}

search_users_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
}
