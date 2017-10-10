# Medium Scraper

Python scraper that finds interesting users from your network to interact with. More specifically, it searches the latest posts of all the users you are following, looks through the responses of those posts and picks out the best ones. The purpose of this scraper is to find active users that have interacted with your network and have had a positive response from the community (over a certain number of recommendations on their response).

## Instructions

Install the package

    sudo pip install requests

Modify line 178 in `scraper.py` to put your username and the minimum number of recommendations on the response

    interesting_users = get_interesting_users('Radu_Raicea', 10)

Run the scraper

    python scraper.py