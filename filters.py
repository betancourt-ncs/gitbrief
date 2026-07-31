
# Direct
def is_direct_eligible(tenant):
    if tenant.direct_webhook_url:
        return True
    else:
        return False


# Social
def is_social_eligible(tenant, event_data):
    # Push event
    if event_data['event_type'] == "push":
        if tenant.social_webhook_url and (event_data['branch'] == event_data['default_branch']):
            return True
        else:
            return False
    else:
        return False
