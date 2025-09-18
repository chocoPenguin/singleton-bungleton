📘 AI Foundry Agent 외부 호출 가이드
REST API 호출 방식
1. get token
- method: post
- url: https://login.microsoftonline.com/3efeebc6-c535-4752-bd40-97f1078c7209/oauth2/v2.0/token
- header:
  - Content-Type: application/x-www-form-urlencoded
- body:
  - grant_type:client_credentials
    client_id:dbee27d5-529b-499c-9f32-e0ebe8f525be
    client_secret:aGV8Q~U0g_fr8gFAjraiIvZiNRjMzbLc_neUCcTl
    scope:https://ai.azure.com/.default
를 요청하여
- 응답: access_token(예시: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSIsImtpZCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSJ9.eyJhdWQiOiJodHRwczovL2FpLmF6dXJlLmNvbSIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzNlZmVlYmM2LWM1MzUtNDc1Mi1iZDQwLTk3ZjEwNzhjNzIwOS8iLCJpYXQiOjE3NTgxODU2OTQsIm5iZiI6MTc1ODE4NTY5NCwiZXhwIjoxNzU4MTg5NTk0LCJhaW8iOiJrMlJnWVBCZnhaZG9ZRlMyeS9HMy84OGpQRGR2QUFBPSIsImFwcGlkIjoiZGJlZTI3ZDUtNTI5Yi00OTljLTlmMzItZTBlYmU4ZjUyNWJlIiwiYXBwaWRhY3IiOiIxIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvM2VmZWViYzYtYzUzNS00NzUyLWJkNDAtOTdmMTA3OGM3MjA5LyIsImlkdHlwIjoiYXBwIiwib2lkIjoiYTY2ZjNlMDctZWI2MC00OGNjLTk2YzItZDFiNzljM2Q2MTkxIiwicmgiOiIxLkFiNEF4dXYtUGpYRlVrZTlRSmZ4QjR4eUNWOXZwaGpmMnhkTW5kY1dOSEVxbkw1LUFRQy1BQS4iLCJzdWIiOiJhNjZmM2UwNy1lYjYwLTQ4Y2MtOTZjMi1kMWI3OWMzZDYxOTEiLCJ0aWQiOiIzZWZlZWJjNi1jNTM1LTQ3NTItYmQ0MC05N2YxMDc4YzcyMDkiLCJ1dGkiOiJ5dGg2eUJTYUdrT3RxVUoybndwMUFBIiwidmVyIjoiMS4wIiwieG1zX2Z0ZCI6InBqZzNvZHZDYnhnMzZZa2dwYTJhSWx6a3JhNWM3UndITzFQYUx6NG5YUUFCWVhOcFlYTnZkWFJvWldGemRDMWtjMjF6IiwieG1zX2lkcmVsIjoiNyAyMiIsInhtc19yZCI6IjAuNDJMallCSmkyc2NvSk1MQkxpUndMLVRkNUItZnJSejYtQUtXX0hZd19nb1U1UlFTbUh6cnEwdnVKa25uM2ZjN0l6Tk1tbThDUlRtRUJPTHpsMG5jdnkzdU1fZTZtRW1oMXB4OUFBIn0.cR6vYQUVfTL8B8wOk3Vjd-mBujABtvepdSYxSqwi2PwT5Uip4z6rzG2jUiXEmHb-40X0dKIyblyyXqt8cvYwp9NlL0ocdDdEe9HCpVnVa0fPViM3AEoGXnfHduk0hYiK9B7SwSIQpDoMadGlIInx-GA9c6cYWtHRGFatHDhkMrPpa6l_Nz9Z0FxmFuNEkTQ2wsrHnZTwbrnH6wQaGcRhIAVVDkEihh5G8gob-IwyDZReoUgFM614QEDuxgZ5jal_tPLvi5j52o4u0iesC0UdONKaTw5hT4OkvAvDmYdkiAaq1R_ct-zP_tVmdyUzdafsX2erklVhzJcOk__jp6obPA) 를 저장한다.
2. get thread
- method: post
- url: https://yesong.services.ai.azure.com/api/projects/yesong-project/threads?api-version=v1
- header:
   - Content-Type: application/json
   - Authorization: bearer {1. get token 에서 수신한 access_toekn}
- body: N/A
를 요청하여
- 응답: {
  "id": "thread_lbfhdlUMphobjJsW0ob9ue0i",
  "object": "thread",
  "created_at": 1758186133,
  "metadata": {},
  "tool_resources": {}
  }
중 thread id "id": "thread_lbfhdlUMphobjJsW0ob9ue0i" 를 저장한다.
3. Set Message
- method: POST
- url: https://yesong.services.ai.azure.com/api/projects/yesong-project/threads/{2 에서 수신한 thread id}/messages?api-version=v1
- header:
  - Content-Type:application/json
  - Authorization: bearer {1. get token 에서 수신한 access_toekn}
- body:
  - {
    "role": "user",
    "content": "{퀴즈 생성 요청 프롬프트}"
    }
- 응답: {
  "id": "msg_cwwx89dRLDIZRLsGpY9eYuzr",
  "object": "thread.message",
  "created_at": 1758186305,
  "assistant_id": null,
  "thread_id": "thread_ddq1g9C9Yc046sYRn4H5pyXI",
  "run_id": null,
  "role": "user",
  "content": [
  {
  "type": "text",
  "text": {
  "value": "오늘 날씨 알려줘.",
  "annotations": []
  }
  }
  ],
  "attachments": [],
  "metadata": {}
  }
4. run(메시지 전송)
- method: POST
- url: https://yesong.services.ai.azure.com/api/projects/yesong-project/threads/{2 에서 수신한 thread id}/runs?api-version=v1
- header:
  - Content-Type:application/json
  - Authorization: bearer {1. get token 에서 수신한 access_toekn}
- body:
  - {
    "assistant_id": "{미리 정의된 agent_id}}",
    "stream": true
    }
- 응답은 실패가 아닌 경우 무시한다.
5. Get Result(AI Agent의 응답 수신)
- method: GET
- url: https://yesong.services.ai.azure.com/api/projects/yesong-project/threads/{2 에서 수신한 thread id}/messages?api-version=v1
- header:
  - Authorization: bearer {1. get token 에서 수신한 access_toekn}
- 응답
  - {
    "object": "list",
    "data": [
    {
    "id": "msg_mjUndsvJZJxqhp3vIro1sdKW",
    "object": "thread.message",
    "created_at": 1758186706,
    "assistant_id": "asst_B3eh4Xf6dyowl2M8gNkjazHy",
    "thread_id": "thread_sMUhQOIVzaDmHqGuwAS64Of8",
    "run_id": "run_DTRUP3UQqwRkIP8Rt6bX81ur",
    "role": "assistant",
    "content": [
    {
    "type": "text",
    "text": {
    "value": "오늘 전국적으로 흐리고 지역에 따라 소나기와 약한 비가 내릴 수 있습니다. 서울 기준으로는 오전부터 비가 약하게 내릴 수 있으며, 낮 최고기온은 29~31도 정도로 예상되고 습도도 높아 체감 온도는 더 높게 느껴질 수 있습니다. 전국적으로 폭염 주의보가 발효 중인 곳도 있으니 건강에 유의하세요. 바람은 남서풍이 약하게 불고 습도가 높아 다소 후덥지근한 날씨입니다【3:0†source】.",
    "annotations": [
    {
    "type": "url_citation",
    "text": "【3:0†source】",
    "start_index": 203,
    "end_index": 215,
    "url_citation": {
    "url": "https://www.weather.go.kr/weather/main.jsp",
    "title": "홈 - 기상청 날씨누리"
    }
    }
    ]
    }
    }
    ],
    "attachments": [],
    "metadata": {}
    },
    {
    "id": "msg_l9HlZeYszi4dYiaqUHUT71u7",
    "object": "thread.message",
    "created_at": 1758186698,
    "assistant_id": null,
    "thread_id": "thread_sMUhQOIVzaDmHqGuwAS64Of8",
    "run_id": null,
    "role": "user",
    "content": [
    {
    "type": "text",
    "text": {
    "value": "오늘 날씨 알려줘.",
    "annotations": []
    }
    }
    ],
    "attachments": [],
    "metadata": {}
    }
    ],
    "first_id": "msg_mjUndsvJZJxqhp3vIro1sdKW",
    "last_id": "msg_l9HlZeYszi4dYiaqUHUT71u7",
    "has_more": false
    }
중 data: content: value: 의 값이 퀴즈 문제 본문일 것이다.