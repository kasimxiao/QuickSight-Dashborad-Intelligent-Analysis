import urllib, json, sys
import requests
import boto3 

def get_sts_url(role_arn):
    sts_connection = boto3.client('sts')
    assumed_role_object = sts_connection.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumeRoleSession",
    )

    # Step 3: Format resulting temporary credentials into JSON
    url_credentials = {}
    url_credentials['sessionId'] = assumed_role_object.get('Credentials').get('AccessKeyId')
    url_credentials['sessionKey'] = assumed_role_object.get('Credentials').get('SecretAccessKey')
    url_credentials['sessionToken'] = assumed_role_object.get('Credentials').get('SessionToken')
    json_string_with_temp_credentials = json.dumps(url_credentials)

    # Step 4. Make request to AWS federation endpoint to get sign-in token. Construct the parameter string with
    # the sign-in action request, a 12-hour session duration, and the JSON document with temporary credentials 
    # as parameters.
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration=300"
    if sys.version_info[0] < 3:
        def quote_plus_function(s):
            return urllib.quote_plus(s)
    else:
        def quote_plus_function(s):
            return urllib.parse.quote_plus(s)
    request_parameters += "&Session=" + quote_plus_function(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url)
    # Returns a JSON document with a single element named SigninToken.
    signin_token = json.loads(r.text)

    # Step 5: Create URL where users can use the sign-in token to sign in to 
    # the console. This URL must be used within 15 minutes after the
    # sign-in token was issued.
    request_parameters = "?Action=login" 
    request_parameters += "&Issuer=Example.org" 
    request_parameters += "&Destination=" + quote_plus_function("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    return request_url
