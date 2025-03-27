from api.v1.routes.responses.responses_parts.content.error_contents import error_content
from api.v1.routes.responses.responses_parts.content.user_contents import (
    user_model_content,
)


user_not_found_response = {404: {**error_content, "description": "User not found"}}

user_already_exists_response = {
    409: {**error_content, "description": "User already exists"}
}

user_created_response = {
    201: {**user_model_content, "description": "User successfully created"}
}
