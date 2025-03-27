from api.v1.routes.responses.responses_parts.content.error_contents import error_content

login_failed_response = {401: {**error_content, "description": "Login failed"}}

refresh_failed_response = {
    401: {**error_content, "description": "Refresh token failed"}
}

check_permission_failed_response = {
    403: {**error_content, "description": "Access to resource denied"}
}

check_permission_error_response = {
    401: {**error_content, "description": "Invalid access token"}
}

logout_error_response = {401: {**error_content, "description": "Invalid access token"}}
