
import requests
import json


# Removes the extra characters that get returned with every JSON request on Medium endpoints
def clean_json_response(response):
    return json.loads(response.text.split('])}while(1);</x>')[1])


# Returns the User ID of a Medium Username
def get_user_id(username):
    response = requests.get('https://medium.com/@' + username + '?format=json')
    response_dict = clean_json_response(response)
    return response_dict['payload']['user']['userId']


# Returns the list of Usernames from a user's Followings list
def get_list_of_followings(user_id):
    
    next_id = False
    followings = []

    while True:

        if next_id:
            response = requests.get('https://medium.com/_/api/users/' + user_id + '/following?limit=8&to=' + next_id)
        else:
            response = requests.get('https://medium.com/_/api/users/' + user_id + '/following')

        response_dict = clean_json_response(response)

        for user in response_dict['payload']['value']:
            followings.append(user['username'])

        try:
            next_id = response_dict['payload']['paging']['next']['to']
        except:
            break

    return followings


# Returns the list of IDs of the latest posts of a list of users
def get_list_of_latest_posts_ids(usernames):

    post_ids = []

    for username in usernames:
        response = requests.get('https://medium.com/@' + username + '/latest?format=json')
        response_dict = clean_json_response(response)

        try:
            posts = response_dict['payload']['references']['Post']
        except:
            posts = []

        if posts:
            for key in posts.keys():
                post_ids.append(posts[key]['id'])

    return post_ids


# Returns the list of post responses of a list of posts
def get_post_responses(posts):

    responses = []

    for post in posts:
        response = requests.get('https://medium.com/_/api/posts/' + post + '/responses')
        response_dict = clean_json_response(response)
        responses += response_dict['payload']['value']

    return responses


# Checks if a response is over a certain number of recommends
def check_if_high_recommends(response, recommend_min):
    if response['virtuals']['recommends'] >= recommend_min:
        return True


# Returns the list of User IDs of a list of responses that have over a certain number of recommends
def get_user_ids_from_responses(responses, recommend_min):
    
    user_ids = []

    for response in responses:
        if check_if_high_recommends(response, recommend_min):
            user_ids.append(response['creatorId'])

    return user_ids


# Returns the list of usernames of a list of User IDs
def get_usernames(user_ids):

    usernames = []

    for user_id in user_ids:
        response = requests.get('https://medium.com/_/api/users/' + user_id)
        response_dict = clean_json_response(response)
        usernames.append(response_dict['payload']['value']['username'])

    return usernames


# Returns a list of usernames in your network that might be interesting to interact with
def get_recommended_users(username, recommend_min):

    user_id = get_user_id(username)

    usernames = get_list_of_followings(user_id)

    posts = get_list_of_latest_posts_ids(usernames)

    responses = get_post_responses(posts)

    users = get_user_ids_from_responses(responses, recommend_min)

    return get_usernames(users)


print(get_recommended_users('Radu_Raicea', 5))
