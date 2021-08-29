import boto3
import json
import random
import requests
from urllib.request import urlopen, Request
import urllib
from pprint import pprint

# DataOps topic
jandi_url = "{Jandi_Incoming_Webhook_URL}"
weather_desc = {
    "Thunderstorm": "오늘은 천둥 번개네요... 이불밖은 위험한데... ㄷㄷ",
    "Drizzle": "오늘은 비가 오네요. 우산들은 다들 챙기셨죠?",
    "Rain": "오늘은 비가 오네요. 우산들은 다들 챙기셨죠?",
    "Snow": "오늘은 눈이 오네요 Do you want to build a snowman~?",
    "Atmosphere": "오늘은 마스크 꼭꼭 잘 쓰고 다녀야겠어요!",
    "Clear": "오늘은 날씨가 맑음이랍니다. 점심 식사 후 산책 어떠세요?",
    "Clouds": "오늘은 날씨가 많이 흐리네요... 오늘 업무는 상쾌한 음악과 함께 어떠실까요?"
}


def lambda_handler(event, context):
    # TODO implement
    print(event['team'])
    if event['team'].lower() == "dataops":
        alert_message(event['namelist'])
    else:
        report_check(event)


def report_check(event):
    title = ""
    if len(event['namelist']) > 0:
        title = """오늘도 고생많으셨습니다! \n현재까지 {} 팀 주간보고 미작성 인원은 다음과 같습니다.\n\n{}
날짜와 이름 기준으로 확인됩니다. 
작성했는데 명단에 계신 분은 하단 내용을 올바르게 기입하셨는 지 확인하시면 됩니다.
1. 금일 날짜 작성
2. 날짜 포맷 : yyyyMMdd
3. 이름

미작성 인원들은 서둘러 작성 부탁드립니다!!!""".format(event['team'], event['namelist'])
    else:
        title = "오늘도 고생많으셨습니다! \n금주 {} 팀 주간보고 미작성 인원은 없습니다.".format(
            event['team'])

    payloads = {
        "body": title,
        "connectColor": "#FAC11B",
    }
    response = requests.post(
        jandi_url, data=json.dumps(payloads),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to jandi returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def alert_message(namelist):
    weather_message = get_weather("Seoul")
    good_message = get_random_messages()
    member_message = get_random_members(namelist)

    title = "{}\n금주도 고생많으셨습니다! \n잊지말고 18시 전까지 주간보고 작성 부탁드리겠습니다.^^\n{}\n{}".format(
        weather_message, member_message, good_message)
    payloads = {
        "body": title,
        "connectColor": "#FAC11B",
    }
    response = requests.post(
        jandi_url, data=json.dumps(payloads),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to jandi returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


def get_random_messages():
    json_data = open('good.json', encoding='UTF8').read()
    datas = json.loads(json_data)
    random.shuffle(datas)
    tmp = list(random.sample(datas, 1)[0].values())[0]
    return tmp


def get_random_members(all_user_list):
    x = random.randint(0, len(all_user_list)-1)
    msg = "{} 님 주간보고 잊지 않으셨죠?\n".format(all_user_list[x])
    return msg


def get_weather(location):
    # Enter your API key here
    api_key = "{Open_weather_API_KEY}"

    # base_url variable to store url
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # complete url address
    complete_url = base_url + "appid=" + api_key + "&q=" + location

    # get method of requests module
    response = requests.get(complete_url).json()
    weather = response['weather'][0]['main']
    weather_message = weather_desc[weather]
    pprint(weather_message)

    return weather_message
