import json


# Push
def parse_push_event(payload):

    commit_data = [
        {"message": commit["message"],
         "added": commit["added"],
         "removed": commit["removed"],
         "modified": commit["modified"]
         } for commit in payload["commits"]]

    push_data = {
        "repo": payload["repository"]["name"],
        "pusher": payload["pusher"]["name"],
        "branch": payload["ref"].split("/")[-1],
        "default_branch": payload["repository"]["default_branch"],
        "commits": commit_data
    }
    return push_data


# Pull Request
def parse_pr_event(payload):

    pr = payload["pull_request"]

    pr_data = {
        "title": pr["title"],
        "body": pr["body"] or "No description provided",
        "commits": pr["commits"],
        "additions": pr["additions"],
        "deletions": pr["deletions"],
        "changed_files": pr["changed_files"],
        "username": pr["user"]["login"],
        "repo": pr["head"]["repo"]["full_name"],
        "head_branch": pr["head"]["ref"],
        "base_branch": pr["base"]["ref"],
        "pr_number": pr["number"]
    }
    return pr_data


# Release
def parse_release_event(payload):

    release_data = {
        'action': payload['action'],
        'tag_name': payload['release']['tag_name'],
        'target_commitish': payload['release']['target_commitish'],
        'release_name': payload['release']['name'],
        'prerelease': payload['release']['prerelease'],
        'body': payload['release']['body'],
        'html_url': payload['release']['html_url'],
        'author_login': payload['release']['author']['login'],
        'repo': payload['repository']['name']
    }
    return release_data


# test
if __name__ == "__main__":

    with open("sample_release_payload.json") as f:
        payload = json.load(f)

    print(parse_release_event(payload))
