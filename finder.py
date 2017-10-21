
import requests
import json
import csv
from datetime import datetime, timedelta
from time import sleep

MEDIUM = 'https://medium.com'


# Removes the extra characters that get returned with every JSON request on Medium endpoints
def clean_json_response(response):
    return json.loads(response.text.replace('])}while(1);</x>', '', 1))


# Returns the User ID of a Medium Username
def get_user_id(username):

    print('Retrieving user ID...')

    url = MEDIUM + '/@' + username + '?format=json'
    response = requests.get(url)
    response_dict = clean_json_response(response)
    return response_dict['payload']['user']['userId']


# Returns the list of Usernames from a user's Followings list
def get_list_of_followings(user_id):

    print('Retrieving users from Followings...')
    
    next_id = False
    followings = []

    while True:

        if next_id:
            # If this is not the first page of the followings list
            url = MEDIUM + '/_/api/users/' + user_id + '/following?limit=8&to=' + next_id
        else:
            # If this is the first page of the followings list
            url = MEDIUM + '/_/api/users/' + user_id + '/following'

        response = requests.get(url)
        response_dict = clean_json_response(response)

        for user in response_dict['payload']['value']:
            followings.append(user['username'])

        try:
            # If the "to" key is missing, we've reached the end of the list and an exception is thrown
            next_id = response_dict['payload']['paging']['next']['to']
        except:
            break

    return followings


# Returns the list of IDs of the latest posts of a list of users
def get_list_of_latest_posts_ids(usernames):

    print('Retrieving the latest posts...')

    post_ids = []

    for username in usernames:
        url = MEDIUM + '/@' + username + '/latest?format=json'
        response = requests.get(url)
        response_dict = clean_json_response(response)

        try:
            posts = response_dict['payload']['references']['Post']
        except:
            posts = []

        if posts:
            for key in posts.keys():
                post_ids.append(posts[key]['id'])

    return post_ids


# Returns the list of post responses of a list of posts that are no older than 1 month
def get_post_responses(posts):

    print('Retrieving the post responses...')

    responses = []

    for post in posts:
        url = MEDIUM + '/_/api/posts/' + post + '/responses'
        response = requests.get(url)
        response_dict = clean_json_response(response)
        responses += response_dict['payload']['value']
        sleep(0.5) # This is the most intensive operation for the Medium servers, we'll help them out

    return responses


# Checks if a response was created in the last 30 days
def check_if_recent(response):

    limit_date = datetime.now() - timedelta(days=30)
    creation_epoch_time = response['createdAt'] / 1000
    creation_date = datetime.fromtimestamp(creation_epoch_time)

    if creation_date >= limit_date:
        return True


# Checks if a response is over a certain number of recommends
def check_if_high_recommends(response, recommend_min):
    if response['virtuals']['recommends'] >= recommend_min:
        return True


# Returns the list of User IDs of a list of responses that have over a certain number of recommends
def get_user_ids_from_responses(responses, recommend_min):
    
    print('Retrieving user IDs from the responses...')

    user_ids = []

    for response in responses:
        recent = check_if_recent(response)
        high_recommends = check_if_high_recommends(response, recommend_min)
        if recent and high_recommends:
            user_ids.append(response['creatorId'])

    return user_ids


# Returns the list of usernames of a list of User IDs
def get_usernames(user_ids):

    print('Retrieving usernames of interesting users...')

    usernames = []

    for user_id in user_ids:
        url = MEDIUM + '/_/api/users/' + user_id
        response = requests.get(url)
        response_dict = clean_json_response(response)
        usernames.append(response_dict['payload']['value']['username'])

    return usernames


# Adds list of interesting users to the interesting_users.csv and adds a timestamp
def list_to_csv(interesting_users_list):
    with open('interesting_users.csv', 'a') as file:
        writer = csv.writer(file)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        interesting_users_list.insert(0, now)

        writer.writerow(interesting_users_list)


# Returns a list of usernames in your network that might be interesting to interact with
def get_interesting_users(username, recommend_min):

    print('Looking for interesting users for %s...' % username)

    user_id = get_user_id(username)

    usernames = get_list_of_followings(user_id)

    posts = get_list_of_latest_posts_ids(usernames)

    responses = get_post_responses(posts)

    users = get_user_ids_from_responses(responses, recommend_min)

    return get_usernames(users)


interesting_users = get_interesting_users('Radu_Raicea', 10)
print(interesting_users)
list_to_csv(interesting_users)
