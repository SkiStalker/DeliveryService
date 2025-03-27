from api.v1.routes.responses.responses_parts.account_responses_parts import (
    login_failed_response,
    refresh_failed_response,
    logout_error_response,
)
from api.v1.routes.responses.responses_parts.server_responses_parts import (
    internal_error_response,
)


token_responses = {**login_failed_response, **internal_error_response}

refresh_responses = {**refresh_failed_response, **internal_error_response}

logout_responses = {**logout_error_response, **internal_error_response}
