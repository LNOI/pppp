import requests

host="localhost"
port=8672
endpoint="home"
url=f"http://{host}:{port}/{endpoint}"

data={
    "user_id":154824
}
x=requests.post(url=url, json=data)

print(x.text)