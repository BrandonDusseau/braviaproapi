from . import http, system


class bravia():
    def __init__(self, host, passcode):
        self.http_client = http.http(host=host, psk=passcode)
        self.system = system.system(http_client=self.http_client)
