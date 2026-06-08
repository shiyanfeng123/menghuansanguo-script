import urllib.request
import json

url = "https://pypi.org/pypi/psutil/6.1.1/json"
resp = urllib.request.urlopen(url, timeout=30)
data = json.loads(resp.read())

with open(r"E:\project\python\psutil_urls.txt", "w") as f:
    for f_info in data["urls"]:
        fn = f_info["filename"]
        if "cp39" in fn and "win32" in fn:
            f.write(f"{fn}\n  {f_info['url']}\n")
