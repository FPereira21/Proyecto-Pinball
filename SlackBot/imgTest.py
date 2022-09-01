from urllib.request import Request, urlopen
from os import environ


slack_bot_token = environ.get('SLACK_BOT_TOKEN')
url = "https://files.slack.com/files-pri/T03TU752Z1V-F040BMU8Q9Z/pinblo.jpg"
req = Request(url)
req.add_header('Authorization', f'Bearer {slack_bot_token}')
content = urlopen(req).read()
f = open('/home/felipe/Downloads/pinbolo.jpg', 'wb')
f.write(content)
f.close()

