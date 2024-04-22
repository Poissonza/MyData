from torn import UserApi

t_api = UserApi("NPVrnYcFNUJYrYhJ", 100, "poisson")

params = {"selections": "log", "to": 1538046663}

t_api.fetch_josn(params)
