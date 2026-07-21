from API.api import API
from config import Config


class TornAPI(API):

    def __init__(self, category: str, params: dict | None = None):

        if params is None:
            params = {}
        base_address = f"https://api.torn.com/v2/{category}/"
        header = {
            "accept": "application/json",
            "Authorization": f"ApiKey {Config.TORN_API_KEY}",
        }

        super().__init__(base_address, params, header)

    @staticmethod
    def prep_params(**kwargs) -> dict:
        params = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "filters":
                assert v in [
                    "incoming",
                    "outgoing",
                ], f"Invalid filter value: {v}"
            elif k == "sort":
                assert v in ["ASC", "DESC"], f"Invalid sort value: {v}"
            elif k == "striptags":
                assert v in ["true", "false"], f"Invalid striptags value: {v}"
            elif k == "from_ts":
                k = "from"
            elif k == "to_ts":
                k = "to"
            params[k] = v

        return params
