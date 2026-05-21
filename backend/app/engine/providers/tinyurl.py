from app.engine.providers.generic import GenericHandler

class TinyUrlHandler(GenericHandler):
    name = "tinyurl"
    domains = ["tinyurl.com"]
