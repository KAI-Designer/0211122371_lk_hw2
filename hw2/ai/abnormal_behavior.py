import cv2
import requests
import base64
import json

# 百度AI的Access Token
ACCESS_TOKEN = "24.034fd787dcec54ecb3fe696a65532d8c.2592000.1722739941.282335-90878767"

def detect_abnormal_behavior(image):
    # 将OpenCV图像转换为字节数组
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = buffer.tobytes()

    # 将图像转换为base64编码
    image_base64 = base64.b64encode(image_bytes).decode()

    # 百度AI人体检测和属性识别API的URL
    url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/body_attr?access_token={ACCESS_TOKEN}"

    # 请求头和请求数据
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'image': image_base64}

    # 发送请求并获取结果
    response = requests.post(url, headers=headers, data=data)
    result = response.json()

    # 调试输出完整响应
    print("API Response:", json.dumps(result, indent=2, ensure_ascii=False))

    # 处理结果
    for person in result.get('person_info', []):
        attributes = person.get('attributes', {})
        smoking = attributes.get('smoke', {})
        print(f"Detected attributes: {attributes}")  # 调试输出
        if smoking.get('name') == '吸烟' and smoking.get('score', 0) > 0.5:  # 假设0.5是置信度阈值
            location = person.get('location', {})
            return '吸烟', smoking.get('score'), location
    return None, None, None
