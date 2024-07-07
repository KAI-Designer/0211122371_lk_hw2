import base64
import requests
import cv2
from urllib3 import response

access_token = "24.f552e6f08caf013e3792921ecb74c195.2592000.1722733605.282335-90878767"

def capture_face_image():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Convert frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode()

        cv2.imshow('Capturing Face', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return img_str

def register_face(username, img_str):
    url = f"https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "image": img_str,
        "image_type": "BASE64",
        "max_face_num": 1,
        "face_field": "faceshape,facetype"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result['error_code'] == 0:
        face_token = result['result']['face_list'][0]['face_token']
        url = f"https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add?access_token={access_token}"
        payload = {
            "image": img_str,
            "image_type": "BASE64",
            "group_id": "your_group_id",
            "user_id": username,
            "user_info": "User's info"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    else:
        return result

def recognize_face(img_str):
    url = f"https://aip.baidubce.com/rest/2.0/face/v3/search?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "image": img_str,
        "image_type": "BASE64",
        "group_id_list": "your_group_id",
        "max_user_num": 1
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
