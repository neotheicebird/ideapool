import requests
import os
import json
import sys


def signup(event, context):
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "No payload found"
            })
        }

    # get Machine-to-machine access token
    resp = requests.post(
        os.environ['AUTH0_DOMAIN'] + '/oauth/token',
        json={
            'grant_type': 'client_credentials',
            'client_id': os.environ['AUTH0_MANAGEMENT_API_CLIENT_ID'],
            'client_secret': os.environ['AUTH0_MANAGEMENT_API_CLIENT_SECRET'],
            'audience': os.environ['AUTH0_AUDIENCE'],
            'scope': 'create:users'
        },
        headers={
            'content-type': "application/json"
        }
    )

    m2m = resp.json()

    if "access_token" not in m2m:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': m2m['error_description']
            })
        }

    access_token = m2m['access_token']

    payload = {
        'email': body['email'],
        'password': body['password'],
        'name': body.get('name'),
        'email_verified': True,
        'blocked': False,
        'connection': os.environ['AUTH0_CONNECTION'],
    }

    resp = requests.post(
        os.environ['AUTH0_DOMAIN'] + "/api/v2/users",
        json=payload,
        headers={
            'Authorization': 'Bearer {TOKEN}'.format(TOKEN=access_token),
            'content-type': "application/json"
        })

    print("Signup response: ")
    print(resp)
    print(resp.json())

    signup_json = resp.json()

    if "error" in signup_json:
        return {
            'statusCode': signup_json['statusCode'],
            'body': json.dumps({
                'error': signup_json['message']
            })
        }
    else:
        email = signup_json["email"]
        picture = signup_json["picture"]
        name = signup_json["name"]
        user_id = signup_json["identities"][0]["user_id"]

        sys.path.append('base_storage')
        sys.path.append('dynamodb_storage')
        from dynamodb_storage.dynamodb_repository import Respository

        repository = Respository(user_id, os.environ['STAGE'])
        repository.repos['user'].save({
            'email': email,
            'name': name,
            'picture': picture,
            'entity_id': user_id,
        })

        # login

        req = requests.post(
            os.environ['AUTH0_DOMAIN'] + '/oauth/token',
            json={
                'grant_type': 'password',
                'username': email,
                'password': body['password'],
                'audience': os.environ['AUTH0_AUDIENCE'],
                'client_id': os.environ['AUTH0_CLIENT_ID'],
                'client_secret': os.environ['AUTH0_CLIENT_SECRET'],
                'scope': 'openid offline_access'
            }
        )

        login_json = req.json()
        print("Login JSON: ")
        print(login_json)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'jwt': login_json['id_token'],
                'refresh_token': login_json['refresh_token']
            })
        }


def login(event, context):
    # login
    body = event.get('body')

    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': "No payload found"
            })
        }

    if "email" not in body or "password" not in body:
        return {
            'statusCode': 401,
            'body': json.dumps({
                'error': "Bad credentials"
            })
        }

    req = requests.post(
        os.environ['AUTH0_DOMAIN'] + '/oauth/token',
        json={
            'grant_type': 'password',
            'username': body["email"],
            'password': body['password'],
            'audience': os.environ['AUTH0_AUDIENCE'],
            'client_id': os.environ['AUTH0_CLIENT_ID'],
            'client_secret': os.environ['AUTH0_CLIENT_SECRET'],
            'scope': 'openid offline_access'
        }
    )

    login_json = req.json()
    print("Login JSON: ")
    print(login_json)

    return {
        'statusCode': 201,
        'body': json.dumps({
            'jwt': login_json['id_token'],
            'refresh_token': login_json['refresh_token']
        })
    }

