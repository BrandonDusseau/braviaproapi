class system(object):
    def __init__(self, http_client):
        self.http_client = http_client

    def power_on(self):
        self.http_client.request(endpoint="system", method="setPowerStatus", params={"status": True}, version="1.0")

    def power_off(self):
        self.http_client.request(endpoint="system", method="setPowerStatus", params={"status": False}, version="1.0")
