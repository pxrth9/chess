import base64


def decode_token(token):
    return base64.b64decode(token).decode("utf-8")
