
import os
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv(override=True)

url = os.getenv("SMOLVLM_API_URL")
api_key = os.getenv("SMOLVLM_API_KEY", "")

print("Endpoint configured:", bool(url))
print("API key configured:", bool(api_key))

if not url:
    raise SystemExit("SMOLVLM_API_URL is missing from .env")

headers = {}
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

request = urllib.request.Request(
    url,
    headers=headers,
    method="GET",
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        print("HTTP status:", response.status)
        print("The endpoint is reachable.")

except urllib.error.HTTPError as exc:
    # GET may not be supported by this POST-only endpoint.
    # An HTTP response still confirms that a server answered.
    print("HTTP status:", exc.code)
    print("The server responded; GET may not be supported.")

except Exception as exc:
    print("Connection failed:", type(exc).__name__)
    print("Details:", str(exc))
