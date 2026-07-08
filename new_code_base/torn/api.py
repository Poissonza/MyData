from API.api import API

class TornAPI(API):

    def __init__(self, key: str, category:str ,params: dict = None):

        base_address = f"https://api.torn.com/v2/{category}/"
        header = {"accept": "application/json", "Authorization": f"ApiKey {key}"}

        super().__init__(base_address, params, header)

    def prep_params(self, **kwargs) -> dict:
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
            params[k] = v

        return params
