import requests
from github import Github
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("imgtest.html", user_image= "https://www4b.wolframalpha.com/Calculate/MSP/MSP5343175c3he563612h1300001f2dc5bhge4412f4?MSPStoreType=image/gif&amp;s=41")

if __name__ == "__main__":
    app.run()

"""

#9U487H-VALXT3HLLQ -- wolfram Appid
resp = requests.get('https://api.wolframalpha.com/v2/query?input=Academy+award+2019&podstate=Result__More&podstate=Result__More&includepodid=Result&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ').json()
#print(resp['queryresult']['pods'][0]['subpods'][0]['plaintext'])
print(resp)

#use movie list from wolfram to get movie name and search it in new api
movlist = resp['queryresult']['pods'][0]['subpods'][0]['plaintext']
movie = movlist.splitlines()
mov = movie[0].split(' | ')
#mov has award name and winner in indexes 0 & 1 respectively, now using search for ease of access

#using omdb api
search = 'Green Book'
res = requests.get('http://www.omdbapi.com/?apikey=82ddccc8&?t=Green+Book')
print(res.json())



# using username and password
#g = Github("austin.blanchard@utexas.edu", "G00seman$")
# or using an access token
g = Github("42fecb005a67ca016a3ef08fc8935d3281269912")
# Github Enterprise with custom hostname
#g = Github(base_url="https://{databaseApp}/api/v3", login_or_token="42fecb005a67ca016a3ef08fc8935d3281269912")

repo = g.get_repo("SahilAshar/EE461L-DatabaseApp")
#contents = repo.get_clones_traffic()
contents = repo.get_clones_traffic()
print(contents)

#42fecb005a67ca016a3ef08fc8935d3281269912 -- github pers access token
#res = requests.get('https://api.github.com/repos/:ablanchard10/:EE461L-DatabaseApp/stats/contributors')
#print(res.content)

