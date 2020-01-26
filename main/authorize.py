from main.models import GoogleCreds
from googleapiclient.discovery import build
import httplib2

def authorize(Credential, *args):
    if args:
        # Args = ((drive, v3), (gmail, v1))
        assert all(isinstance(x, tuple) for x in args)
        assert all(len(x) == 2 for x in args)
        assert all(all(isinstance(y, str) for y in x) for x in args)

    if isinstance(Credential, GoogleCreds):
        creds = Credential.getCreds()
    else:
        creds = Credential
    http = httplib2.Http()
    http = creds.authorize(http)

    return_dict = {}
    for a in args:
        return_dict[a[0]] = build(a[0], a[1], http=http)

    return return_dict