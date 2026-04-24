from functools import wraps
from typing import Type

from flask import jsonify, request
from pydantic import BaseModel, ValidationError


def validate_request(schema: Type[BaseModel]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return (
                    jsonify(
                        {
                            "error": "Unsupported Media Type",
                            "details": [
                                {"msg": "Request must be JSON", "type": "media_type"}
                            ],
                        }
                    ),
                    415,
                )
            try:
                # Parse and validate the incoming JSON payload
                parsed_data = schema.model_validate(request.get_json())
                # Pass the validated Pydantic object to the route handler
                return f(parsed_data, *args, **kwargs)
            except ValidationError as e:
                # Format Pydantic errors into our standard envelope
                details = [
                    {
                        "loc": [str(loc) for loc in err["loc"]],
                        "msg": err["msg"],
                        "type": err["type"],
                    }
                    for err in e.errors()
                ]
                return jsonify({"error": "Validation Error", "details": details}), 422

        return decorated_function

    return decorator
