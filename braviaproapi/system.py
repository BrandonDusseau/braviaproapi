class system(object):
    def __init__(self, http_client):
        self.http_client = http_client

    def power_on(self):
        self.http_client.request(endpoint="system", method="setPowerStatus", params={"status": True})

    def power_off(self):
        self.http_client.request(endpoint="system", method="setPowerStatus", params={"status": False})

    def is_power_on(self):
        response = self.http_client.request(endpoint="system", method="getPowerStatus")

        if response["status"] == "standby":
            return False

        if response["status"] == "active":
            return True

        raise ValueError("Unexpected getPowerStatys response '{0}'".format(response["status"]))
