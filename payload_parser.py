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
        "default_branch": payload["repository"]["default_branch"],
        "commits": commit_data
    }

    # Checking for branch push vs tag push to assign branch or tag name
    # Slicing using slashes (/) is ineffective if branch name contains one (e.g refs/heads/feature/login)
    ref = payload["ref"]
    if ref.startswith("refs/heads/"):
        push_data["ref_type"] = "heads"
        push_data["branch"] = ref.removeprefix("refs/heads/")
    elif ref.startswith("refs/tags/"):
        push_data["ref_type"] = "tags"
        push_data["branch"] = None
        push_data["tag"] = ref.removeprefix("refs/tags/")

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
