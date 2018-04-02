# Importing libraries
from InstagramAPI import InstagramAPI
import requests
from pathlib import Path
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import textwrap
import json
from datetime import datetime
import calendar
import yaml

# Importing configuration
config = yaml.load(open('./config.yml', 'r'))

# Setting dates
now = datetime.now()
weekday = calendar.day_name[now.weekday()]

# Getting data from API
request = json.loads(requests.get('http://quotes.rest/qod.json').text)
quote = request['contents']['quotes'][0]['quote']
base_url = 'https://api.unsplash.com/photos/random/?query=nature'
img_width = '1080'
img_height = '1080'
img_req_string = '{url}&w={w}&h={h}&client_id={c_id}'.format(url=base_url, w=img_width, h=img_height, c_id=config['client_id'])
image_request = requests.get(img_req_string).json()['urls']['custom']

# Get actual image from api
r = requests.get(image_request, stream=True)
if r.status_code == 200:
    with open('scenery.jpg', 'wb') as f:
        for chunk in r:
            f.write(chunk)
photo = 'scenery.jpg'


# Getting hashtags
def hashtag_converter(array):
        for i in range(len(array)):
                if '-' in array[i]:
                    array[i] = array[i].replace('-', '')
                array[i] = ''.join(('#', array[i]))
        end_string = ' '.join(array)
        return end_string


hashtags = hashtag_converter(request['contents']['quotes'][0]['tags'])

# Setting post title
caption = 'By ' + request['contents']['quotes'][0]['author'] + ' ' + hashtags + ' Have a nice ' + weekday.lower() + '!'

# Logging into instagram with configuration password and username
instagram_user = config['username']
instagram_password = config['password']

ig_api = InstagramAPI(instagram_user, password=instagram_password)
ig_api.login()

# Setting variables for drawing
font_size = 50
font = ImageFont.truetype('arial.ttf', font_size)

# Drawing
img = Path(photo)
if img.is_file():
    img = Image.open(photo)
    draw = ImageDraw.Draw(img)
    MAX_W, MAX_H = img.size
    para = textwrap.wrap(quote, width=45)
    current_h, pad = 50, 10
    for line in para:
        w, h = draw.textsize(line, font=font)
        draw.rectangle([((MAX_W - w) / 2, current_h), ((MAX_W + w) / 2, current_h + h)], fill='rgb(255,255,255)')
        draw.text(((MAX_W - w) / 2, current_h), line, fill='black', font=font)
        current_h = current_h + h + pad
    img.save('image.jpg')

    ig_api.uploadPhoto('image.jpg', caption=caption)

