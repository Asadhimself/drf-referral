# DRF Referral System

Django Referral System is a Django-based application that serves as a template for building referral systems. It utilizes Django Rest Framework for creating RESTful APIs.

## Tech Stack

- Python <img height="20" width="20" src="https://cdn.simpleicons.org/python" />
- Django <img height="20" width="20" src="https://cdn.simpleicons.org/django/white" />
- Django Rest Framework 
- DRF Spectacular (for automatic documentation) <img height="20" width="20" src="https://cdn.simpleicons.org/swagger" />
- PostgreSQL <img height="20" width="20" src="https://cdn.simpleicons.org/postgresql" />
## Description

This app provides a simple foundation for implementing a referral system. It includes a custom user model with authentication.

## Installation
1. Clone repo
```bash
git clone https://github.com/Asadhimself/drf-referral.git
```

2. Install dependecies
```bash
pip install poetry
poetry install
```

3. Rename .env.example to .env and set up your environment dependencies

4. Run migrations
```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

5. Run the app
```bash
python manage.py runserver
```

In localhost:8000/api/docs (it's also home page) you can automatically generated SwaggerUI docs. 

### Request

`POST /api/login/`

```bash
curl -d 'phone_number=+998901234567' http://localhost:8000/api/login/
```

Response:
```
{
  'phone_number': '+998901234567',
  'otp': '1234',
}
```

When you get OTP you can use it only once. After you getting Auth token OTP become useless.

You can get auth token by sending second request:

```bash
curl -X POST \
-H "Content-Type: application/json" \
-d '{"phone_number": "+998901234567", "otp": "1234"}' \
http://localhost:800/api/login/
```

Response:

```
{
	'url_account': '/api/account/',
	'token': 'some-auth-token'
}
```

## Get Account
In order to authenticate you need to puth it into headers like shown in example:

Authorization: Token <place-token-here>

### Request

`GET /api/account/`

	curl -H 'Authorization: Token some-auth-token' http://localhost:8000/api/account/

### Response

	{
		"url_account":"/api/account/",
		"phone_number":"+998901234567",
		"username":"+998901234567",
		"email":"",
		"first_name":"",
		"last_name":"",
		"last_login":"2022-03-30T04:59:02.718663+03:00",
		"date_joined":"2022-03-30T04:59:02.613466+03:00",
		"invite":null,
		"user_invite":{
			"pk":2,
			"key":"some-invite-key",
			"account_set":[]
		}
	}

## Change "username", "email", "first_name", "last_name"

### Request

`PUT /api/account/`

	curl -H 'Authorization: Token some-auth-token' -d 'username=Username' -X PUT http://localhost:8000/api/account/

### Response

	{
		"phone_number":"+998901234567",
		"username":"Username",
		"email":"",
		"first_name":"",
		"last_name":"",
		"last_login":"2024-04-26T03:37:02.5332455+05:00",
		"date_joined":"2024-04-26T03:37:02.5332455+05:00",
		"invite":null,
		"user_invite":{
			"pk":2,
			"key":"some-auth-key",
			"account_set":[]
		}
	}

## Add "invite" (Added once, cannot be changed later)

### Request

`PUT /api/account/`

	curl -H 'Authorization: Token some-auth-token' -d 'invite=user-invite-key' -X PUT http://localhost:8000/api/account/

### Response

	{
		"phone_number":"+998901234567",
		"username":"Username",
		"email":"",
		"first_name":"",
		"last_name":"",
		"last_login":"2022-03-30T04:59:02.718663+03:00",
		"date_joined":"2022-03-30T04:59:02.613466+03:00",
		"invite":"some-invite-key",
		"user_invite":{
			"pk":2,
			"key":"user-invite-key",
			"account_set":[]
		}
	}


## Disclaimer
This project served as a technical exercise for job application, but the employer ceased communication. The technical exercise details can be found [here](https://github.com/Asadhimself/drf-referral/blob/main/tech_exercise.md).
