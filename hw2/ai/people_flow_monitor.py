import requests
import base64

# 百度AI的access_token
ACCESS_TOKEN = "24.f552e6f08caf013e3792921ecb74c195.2592000.1722733605.282335-90878767"

def get_people_flow(image):
    url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis?access_token={ACCESS_TOKEN}"
    image_base64 = base64.b64encode(image).decode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'image': image_base64}

    try:
        response = requests.post(url, headers=headers, data=data)
        if response:
            result = response.json()
            print(result)  # 打印返回结果进行调试
            return result
        else:
            print("No response from API")
            return None
    except Exception as e:
        print(f"Error in get_people_flow: {e}")
        return None
