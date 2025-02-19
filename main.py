from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import re
from instagrapi import Client

app = Flask(__name__)
user = ""  # 初始化 user 变量
client = None  # 初始化 OpenAI 客户端对象

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv('API_KEY'))


def process_and_upload_to_instagram(user_text):
    global user, client
    user = user_text

    # 使用 user 进行你的处理
    ai_response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[
        {"role": "user", "content": "你是服務於濱江匿名網5.0的文字小編，請在68字內簡單幽默的回答「%s」這篇匿名訊息。" % (user)}
    ])
    ai_response = re.search(r"content='(.*?)', role", str(ai_response))
    ai = str(ai_response.group(1))
    print(ai)
    user = user.replace('\n', ' ')
    user = [user[i:i + 14] for i in range(0, len(user), 14)]
    user = "\n".join(user)
    ai = ai.replace('\n', ' ')
    ai = [ai[i:i + 17] for i in range(0, len(ai), 17)]
    ai = "\n".join(ai)
    # 打開圖片、繪制文本、保存圖片等代码
    image = Image.open('public/ins.jpg')
    draw = ImageDraw.Draw(image)

    # 加載一個支持中文的字體
    font_path = "public/NotoSansTC-Regular.ttf"  # 替換成你的中文字體路徑
    font = ImageFont.truetype(font_path, size=66)  # 設置字體大小

    # 繪制文本
    text_position_user = (50, 66)  # 調整文字的位置
    text_color = 'rgb(255, 255, 255)'  # 設定文字顏色
    draw.text(text_position_user, user, fill=text_color, font=font)

    font = ImageFont.truetype(font_path, size=56)
    text_position_ai = (50, 700)  # 調整文字的位置
    draw.text(text_position_ai, ai, fill=text_color, font=font)

    # 保存圖片
    image.load()
    background = Image.new("RGB", image.size, (255, 255, 255))
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel

    background.save('public/ready.jpg', 'JPEG', quality=80)

    # 上传图片到 Instagram
    cl = Client()
    cl.login(os.getenv('USERNAME'), os.getenv('PASSWORD'))
    media = cl.photo_upload(
        "public/ready.jpg",
        "濱江匿名網5.0",
        extra_data={
            "custom_accessibility_caption": "alt text example",
            "like_and_view_counts_disabled": 0,
            "disable_comments": 0,
        }
    )
    media.dict()
    print("上傳了")


@app.route('/process-user', methods=['POST', 'OPTIONS'])
def process_user_route():
    if request.method == 'OPTIONS':
        response = app.response_class(
            response='',
            status=200,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
        print(response)
        return response

    user_text = request.json.get('user')
    process_and_upload_to_instagram(user_text)


if __name__ == '__main__':
    app.run(debug=True)
