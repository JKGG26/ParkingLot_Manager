import json


def get_post_params(request, params_required) -> tuple:
    params_gotten = {}
    for param in params_required:
        try:
            params_gotten[param] = request.POST.get(param)
            if params_gotten[param] is None or str(params_gotten[param]) == '':
                raise ValueError()
        except:
            return {}, f"Param '{param}' required"
    
    return params_gotten, None


def get_json_body(request) -> dict:
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        return data
    except json.JSONDecodeError:
        return {}