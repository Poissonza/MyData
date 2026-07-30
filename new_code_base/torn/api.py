from API.api import API


class TornAPI(API):

    def __init__(self, key: str, category: str, params: dict | None = None):

        if params is None:
            params = {}
        base_address = f"https://api.torn.com/v2/{category}/"
        header = {
            "accept": "application/json",
            "Authorization": f"ApiKey {key}",
        }

        super().__init__(base_address, params, header)

    @staticmethod
    def prep_params(**kwargs) -> dict:
        params = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "filters":
                if v not in ["incoming", "outgoing"]:
                    raise ValueError(f"Invalid filter value: {v}")
            elif k == "sort":
                if v not in ["ASC", "DESC"]:
                    raise ValueError(f"Invalid sort value: {v}")
            elif k == "striptags":
                if v not in ["true", "false"]:
                    raise ValueError(f"Invalid striptags value: {v}")
            elif k == "from_ts":
                k = "from"
            elif k == "to_ts":
                k = "to"
            params[k] = v

        return params
