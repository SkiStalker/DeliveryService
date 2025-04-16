from api.v1.routes.responses.responses_parts.server_responses_parts import (
    internal_error_response,
)
from api.v1.routes.responses.responses_parts.account_responses_parts import (
    check_permission_error_response,
    check_permission_failed_response,
)

from api.v1.routes.responses.responses_parts.delivery_responses_parts import (
    delivery_not_found_response,
    delivery_created_response,
)

get_delivery_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
}

create_delivery_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
    **delivery_created_response,
}

update_delivery_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
    **delivery_not_found_response,
}

search_deliveries_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
}
