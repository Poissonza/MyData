import requests

class Api:

    def __init__(self, key, request_limit: int):

        self._request_limit = request_limit
        self._end_point = "https://api.torn.com/"
        self._key = key


    def fetch_josn(self, params: dict):
        params.update({"key": self._key})
        request = requests.get(self._end_point, params)

        print(request.url)


class UserApi(Api):

    def __init__(self, key, request_limit: int, user_id=None):

        super().__init__(key, request_limit)

        if user_id:
            self._end_point = self._end_point + "user/" + str(user_id)
        else:
            self._end_point = self._end_point + "user/"


# https://api.torn.com/users/poisson?selections=log&to=1538046663&key=NPVrnYcFNUJYrYhJ
# https://api.torn.com/user/poisson?selections=log&key=NPVrnYcFNUJYrYhJ&to=1538046663