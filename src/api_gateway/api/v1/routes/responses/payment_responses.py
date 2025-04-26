from api.v1.routes.responses.responses_parts.server_responses_parts import (
    internal_error_response,
)
from api.v1.routes.responses.responses_parts.account_responses_parts import (
    check_permission_error_response,
    check_permission_failed_response,
)

from api.v1.routes.responses.responses_parts.payment_responses_parts import (
    delivery_not_found_response,
    payment_rule_created_response
)

make_payment_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
    **delivery_not_found_response
}

accept_payment_responses = {
    **internal_error_response
}

search_payments_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
}

add_payment_rule_responses = {
    **internal_error_response,
    **check_permission_error_response,
    **check_permission_failed_response,
    **payment_rule_created_response
}
