from app.api import API


class TornAPI(API):

    def __init__(self, key: str, category: str, comment: str = "python"):
        header = {"accept": "application/json", "Authorization": f"ApiKey {key}"}
        base_address = f"https://api.torn.com/v2/{category}/"
        params = {"comment": comment}
        super().__init__(base_address=base_address, params=params, header=header)

    def get_torn_data(self, path: str, **kwargs) -> dict:
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
            params[k] = v
        return self.get_json(path, params)
