import base64
import requests

image_path = r"F:\MCA\Mini project\nine_11.png"

with open(image_path, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image accurately. Describe only what is visibly present.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    },
                },
            ],
        }
    ],
    "temperature": 0.1,
    "max_tokens": 300,
}

response = requests.post(
    "http://127.0.0.1:8081/v1/chat/completions",
    json=payload,
    timeout=120,
)

print(response.status_code)
print(response.json()["choices"][0]["message"]["content"])