from jose import jwt
import os
import json
from six.moves.urllib.request import urlopen

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN'][8:]
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
ALGORITHMS = ["RS256"]


def generate_authorizer_response(method, user_id):
    resp = {
        "principalId": user_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": method
                }
            ]
        },
        "context": {
            "user_id": user_id
        }
    }
    print("generated policy: ")
    print(resp)
    return resp


class AuthError(Exception):
    pass


def verify_token(token):
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_CLIENT_ID,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )
            print("Auth Payload:")
            print(payload)
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                            "description":
                                "incorrect claims,"
                                "please check the audience and issuer"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Unable to parse authentication"
                                " token."}, 401)

    raise AuthError({"code": "invalid_header",
                    "description": "Unable to find appropriate key"}, 401)


def auth(event, context):
    print(event)
    print(context)
    token = event.get('authorizationToken')
    method = event.get('methodArn')

    auth_payload = verify_token(token)
    user_id = auth_payload["sub"][6:]
    print(user_id)
    resp = generate_authorizer_response(method, user_id)

    return resp

