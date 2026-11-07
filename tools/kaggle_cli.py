"""Kaggle CLI wrapper for proxy-injected credentials.

The stock CLI validates the access token by POSTing it in a request body
(token introspection). In this sandbox the real token is injected by the
network proxy into the Authorization header only, so introspection fails.
This wrapper skips introspection and trusts the header-injected token.

Usage: KAGGLE_USERNAME=<your kaggle username> python tools/kaggle_cli.py kernels list --mine
"""
import os
import sys

os.environ.setdefault("KAGGLE_API_TOKEN", "proxy-injected")

from kaggle.api.kaggle_api_extended import KaggleApi  # noqa: E402

_username = os.environ.get("KAGGLE_USERNAME", "unknown")
KaggleApi._introspect_token = lambda self, token: _username

from kaggle.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
