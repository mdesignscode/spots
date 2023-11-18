from pyyoutube import Client as YTClient
yt_client = YTClient(api_key="AIzaSyCcP8I5KvsxTsHOEF_GkKwoy_-E5qYK00k")
query = yt_client.search.list("snippet", q="Doja Cat - Mooo!")
print(query.to_dict()["items"][0])
