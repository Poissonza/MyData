from API.api import API

class TornAPI(API):

    def __init__(self, key: str, category:str ,params: dict = None):

        base_address = f"https://api.torn.com/v2/{category}/"
        header = {"accept": "application/json", "Authorization": f"ApiKey {key}"}

        super().__init__(base_address, params, header)

