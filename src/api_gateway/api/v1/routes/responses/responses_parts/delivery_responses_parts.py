from api.v1.routes.responses.responses_parts.content.error_contents import error_content
from api.v1.routes.responses.responses_parts.content.delivery_contents import (
    delivery_model_content,
)


delivery_not_found_response = {404: {**error_content, "description": "Delivery not found"}}

delivery_created_response = {
    201: {**delivery_model_content, "description": "Delivery successfully created"}
}
