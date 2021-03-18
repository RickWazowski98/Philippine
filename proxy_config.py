

def get_proxy():
    host = "hub.zenscrape.com"
    port = "31112"
    username = "81ztb0hcg6er357"
    password = "UlaniAt2YrbGYpbV"
    country_param = "_country-Indonesia"
    http_proxy = f"http://{username}:{password}{country_param}@{host}:{port}"

    proxy_dict = {
        "http": http_proxy,
        "https": http_proxy
    }
    return proxy_dict
