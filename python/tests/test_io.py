#  Copyright 2021 Rikai Authors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import base64
from io import BytesIO

import numpy as np
import PIL
import requests
import requests_mock

from rikai.conf import CONF_RIKAI_IO_HTTP_AGENT, get_option
from rikai.io import open_uri
from rikai.types.vision import Image

WIKIPEDIA = (
    "https://upload.wikimedia.org/wikipedia/commons/a/ad/"
    "Commodore_Grace_M._Hopper%2C_USN_%28covered%29.jpg"
)

USER_AGENT = "User-Agent: Rikai/0.0.10 (rikai-dev@eto.ai)"


def test_open_https_uri():
    """Test support of https URI"""

    with open_uri(WIKIPEDIA) as fobj:
        assert len(fobj.read()) > 0


def test_image_use_https_uri():
    img = Image(WIKIPEDIA)

    fobj = BytesIO(
        requests.get(WIKIPEDIA, headers={"User-agent": USER_AGENT}).content
    )
    pic = PIL.Image.open(fobj)
    assert np.array_equal(img.to_numpy(), np.array(pic))


def test_simple_http_credentials():
    with requests_mock.Mocker() as mock:
        mock.get("http://test.com", text="{}")
        requests.get("http://test.com", auth=("user", "def_not_pass"))
        req = mock.request_history[0]
        assert req.headers.get("Authorization") == "Basic {}".format(
            base64.b64encode(b"user:def_not_pass").decode("utf-8")
        )


def test_no_http_credentials():
    with requests_mock.Mocker() as mock:
        mock.get("http://test.com", text="{}")
        requests.get("http://test.com")
        req = mock.request_history[0]
        assert "Authorization" not in req.headers
