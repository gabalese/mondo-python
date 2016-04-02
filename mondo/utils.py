from urllib import parse


def build_url(root: str, folder: str = "/", querystring: dict = None):
    if not querystring:
        querystring = {}
    return "{}/{}?{}".format(
        root, folder, parse.urlencode(querystring)
    )
