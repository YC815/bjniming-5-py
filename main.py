from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import re
from instagrapi import Client
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # 允許所有來源請求

user = ""  # 初始化 user 变量
client = None  # 初始化 OpenAI 客户端对象

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv('API_KEY'))


def process_and_upload_to_instagram(user_text):
    global client

    # 生成 AI 回應
    try:
        ai_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"你是服務於濱江匿名網5.0的文字小編，請在68字內簡單幽默的回答「{user_text}」這篇匿名訊息。"}
            ]
        )
        if ai_response and ai_response.choices:
            ai = ai_response.choices[0].message.content.strip()
        else:
            ai = "無法生成回應，請稍後再試。"
    except Exception as e:
        print(f"AI 回應錯誤: {e}")
        ai = "發生錯誤，請稍後再試。"

    print(f"AI 回應: {ai}")

    # 格式化使用者輸入與 AI 回應
    user_text = user_text.replace('\n', ' ')
    user_text = "\n".join([user_text[i:i + 14] for i in range(0, len(user_text), 14)])
    ai = ai.replace('\n', ' ')
    ai = "\n".join([ai[i:i + 17] for i in range(0, len(ai), 17)])

    # 打開圖片，繪制文本
    try:
        image = Image.open('public/ins.jpg')
        draw = ImageDraw.Draw(image)
        font_path = "public/NotoSansTC-Regular.ttf"  # 確保字體存在
        font_user = ImageFont.truetype(font_path, size=66)
        font_ai = ImageFont.truetype(font_path, size=56)

        # 繪制使用者文字
        draw.text((50, 66), user_text, fill='rgb(255, 255, 255)', font=font_user)
        # 繪制 AI 回應
        draw.text((50, 700), ai, fill='rgb(255, 255, 255)', font=font_ai)

        # 保存圖片
        image.load()
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        background.save('public/ready.jpg', 'JPEG', quality=80)
    except Exception as e:
        print(f"圖片處理錯誤: {e}")
        return

    # 上傳圖片到 Instagram
    try:
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
        print("上傳成功！")
    except Exception as e:
        print(f"Instagram 上傳錯誤: {e}")


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
        return response

    user_text = request.json.get('user')

    try:
        process_and_upload_to_instagram(user_text)
        return jsonify({"message": "成功處理並上傳到 Instagram"}), 200
    except Exception as e:
        print(f"API 錯誤: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
