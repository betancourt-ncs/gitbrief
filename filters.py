
# Direct
def is_direct_eligible(tenant):
    if tenant.direct_webhook_url:
        return True
    else:
        return False


# Social
def is_social_eligible(tenant, parsed_data):
    if not tenant.social_webhook_url:
        return False

    # Push event main branch check
    if parsed_data['event_type'] == "push":
        return parsed_data['branch'] == parsed_data['default_branch']

    return True
