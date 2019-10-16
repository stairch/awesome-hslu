from datetime import datetime
import requests
import json
import operator


GITHUB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATA_FILE = 'students.json'


def get_update_check_data():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    return data


def update_last_check():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    data["last_check"] = datetime.now().strftime(GITHUB_DATETIME_FORMAT)

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


def to_datetime(string_datetime):
    return datetime.strptime(string_datetime, GITHUB_DATETIME_FORMAT)


def check_for_new_repos_by_known_students():
    update_check_data = get_update_check_data()
    last_checked = to_datetime(update_check_data["last_check"])
    print("last checked: {}".format(last_checked))

    for user in update_check_data["students"]:

        print("checking repos of {}...".format(user))

        # get all repos of a user and sort them by date for early stopping
        r = requests.get('https://api.github.com/users/{}/repos?per_page=20'.format(user))

        if r.status_code == 403:
            print("ERROR: rate limit of 60 requests per hour reached. try again later.")
            return

        if r.status_code == 404:
            print("ERROR: the user {} seems to be deleted from GitHub".format(user))
        else:
            repos = sorted(r.json(), key=operator.itemgetter("created_at"), reverse=True)
            for repo in repos:
                if to_datetime(repo["created_at"]) > last_checked:
                    print(repo["html_url"])
                else:
                    # all not checked repos are older, stop
                    break

    update_last_check()


if __name__ == "__main__":
    check_for_new_repos_by_known_students()
