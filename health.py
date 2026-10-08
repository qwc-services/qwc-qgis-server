import os
import sys
import requests


def get_capabilities(project: str) -> bool:
    port = os.environ.get("PORT", "80")
    url = f"http://127.0.0.1:{port}/ows/{project}"
    params = {
        "SERVICE": "WMS",
        "REQUEST": "GetCapabilities",
    }
    try:
        response = requests.head(url, params=params, timeout=10)
        return response.ok
    except requests.exceptions.Timeout:
        return False


def main() -> None:
    projects = [
        p.strip()
        for p in os.environ.get("QGIS_PRELOAD_PROJECTS", "").split(",")
        if p.strip()
    ]
    ok = all(get_capabilities(p) for p in projects)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
