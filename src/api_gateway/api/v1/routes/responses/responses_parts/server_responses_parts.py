from api.v1.routes.responses.responses_parts.content.error_contents import error_content

internal_error_response = {
    500: {**error_content, "description": "Internal server error"}
}
