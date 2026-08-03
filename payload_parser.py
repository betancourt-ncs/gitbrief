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
    pass


# test
if __name__ == "__main__":

    with open("sample_payload.json") as f:
        payload = json.load(f)

    print(parse_push_event(payload))
