from api.v1.routes.responses.responses_parts.content.error_contents import error_content
from api.v1.routes.responses.responses_parts.content.cargo_contents import (
    cargo_model_content,
)


cargo_not_found_response = {404: {**error_content, "description": "Cargo not found"}}

cargo_created_response = {
    201: {**cargo_model_content, "description": "Cargo successfully created"}
}
