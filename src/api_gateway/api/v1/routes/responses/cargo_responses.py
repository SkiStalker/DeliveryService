from api.v1.routes.responses.responses_parts.server_responses_parts import (
    internal_error_response,
)
from api.v1.routes.responses.responses_parts.account_responses_parts import (
    check_permission_error_response,
    check_permission_failed_response,
)

from api.v1.routes.responses.responses_parts.cargo_responses_parts import (
    cargo_not_found_response,
    cargo_created_response,
)

create_cargo_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **cargo_created_response,
    **internal_error_response,
}

get_user_cargos_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
}

get_cargo_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **cargo_not_found_response,
}

update_cargo_responses = {
    **check_permission_error_response,
    **check_permission_failed_response,
    **internal_error_response,
    **cargo_not_found_response,
}

