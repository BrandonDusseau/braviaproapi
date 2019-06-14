from enum import Enum
from .errors import HttpError, BraviaApiError
from .util import coalesce_none_or_empty


# Error code definitions
class ErrorCode(object):
    ILLEGAL_ARGUMENT = 3
    ERR_CLOCK_NOT_SET = 7
    ILLEGAL_STATE = 7


class AppFeature(Enum):
    UNKNOWN = 0
    TEXT_INPUT = 1
    CURSOR_DISPLAY = 2
    WEB_BROWSE = 3


class AppControl(object):
    def __init__(self, bravia_client, http_client):
        self.bravia_client = bravia_client
        self.http_client = http_client

    def get_application_list(self, exclude_builtin=False):
        self.bravia_client.initialize()

        if type(exclude_builtin) is not bool:
            raise TypeError("exclude_builtin must be a boolean type")

        response = self.http_client.request(endpoint="appControl", method="getApplicationList", version="1.0")

        apps = []
        if response is None:
            return apps

        if type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getApplicationList")

        for app_info in response:
            app = {
                "name": coalesce_none_or_empty(app_info.get("title")),
                "uri": coalesce_none_or_empty(app_info.get("uri")),
                "icon": coalesce_none_or_empty(app_info.get("icon"))
            }

            if exclude_builtin and app["uri"] is not None and "com.sony.dtv.ceb" in app["uri"]:
                continue

            apps.append(app)

        return apps

    def get_application_feature_status(self):
        self.bravia_client.initialize()

        response = self.http_client.request(endpoint="appControl", method="getApplicationStatusList", version="1.0")

        if type(response) is not list:
            raise BraviaApiError("API returned unexpected response format for getApplicationStatusList")

        supported_features = {
            "textInput": AppFeature.TEXT_INPUT,
            "cursorDisplay": AppFeature.CURSOR_DISPLAY,
            "webBrowse": AppFeature.WEB_BROWSE
        }

        enabled_features = {
            AppFeature.TEXT_INPUT: False,
            AppFeature.CURSOR_DISPLAY: False,
            AppFeature.WEB_BROWSE: False
        }

        for feature in response:
            feature_type = supported_features.get(feature["name"], AppFeature.UNKNOWN)

            # Skip unsupported features
            if feature_type == AppFeature.UNKNOWN:
                continue

            enabled_features[feature_type] = True if feature["status"] == "on" else False

        return enabled_features
