"""Minimal local requests-compatible shim with only post()."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass
from urllib import request


@dataclass
class Response:
    text: str

    def json(self):
        return _json.loads(self.text)


def post(url: str, json: dict, timeout: int = 30) -> Response:
    data = _json.dumps(json).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return Response(text=body)
