import requests


class LibCloudRequest(object):
    host = None
    response = None
    object = {}
    user_id = ""
    key = ""

    def __init__(self, user_id, key, secure=True, host=None, port=None,
                 url=None, timeout=None, proxy_url=None,
                 backoff=None, retry_delay=None):
        self.timeout = timeout
        self.user_id = user_id
        self.key = key
        self.host = "{}://{}".format("https" if secure else "http", host)

    def request(self, action, params=None, data=None, headers=None,
                method='GET', raw=False):
        headers["Accept-Encoding"] = "plain"
        self.response = requests.request(
            method=method.lower(),
            url="".join([self.host, action]),
            data=data,
            headers=headers,
            timeout=self.timeout,
            verify=0,
            allow_redirects=1,
            stream=raw,
        )
        if self.response.text:
            self.object = self.response.json()
        else:
            self.object = {}
        return self

    def getresponse(self):
        return self

    def getheaders(self):  # pragma: no cover
        if "content-encoding" in self.response.headers:
            del self.response.headers["content-encoding"]
        return self.response.headers

    @property
    def status(self):
        return self.response.status_code

    @property
    def reason(self):
        return None if self.response.status_code > 400 else self.response.text

    def connect(self):  # pragma: no cover
        pass

    def read(self):
        return self.response.content

    def close(self):  # pragma: no cover
        # return connection back to pool
        self.response.close()
