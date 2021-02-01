def dict_to_item(raw):
    if isinstance(raw, dict):
        resp = {}
        for k, v in raw:
            if isinstance(v, str):
                resp[k] = {
                    'S': v
                }
            elif isinstance(v, int):
                resp[k] = {
                    'I': str(v)
                }
            elif isinstance(v, dict):
                resp[k] = {
                    'M': dict_to_item(v)
                }
            elif isinstance(v, list):
                resp[k] = []
                for i in v:
                    resp[k].append(dict_to_item(i))

        return resp
    elif isinstance(raw, str):
        return {
            'S': raw
        }
    elif isinstance(raw, int):
        return {
            'I': str(raw)
        }
