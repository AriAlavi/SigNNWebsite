

def StorageSystem():
    import time
    from main.models import Profile, TempLocalFile, GoogleFile

    class AuthorizedProfileGenerator():
        def __init__(self):
            self.refreshProfiles()
        def __iter__(self):
            while True:
                if len(self.profiles) == 0:
                    self.refreshProfiles()
                    if len(self.profiles) == 0:
                        yield None
                yield self.profiles.pop()

        def refreshProfiles(self):
            self.profiles = [x for x in Profile.objects.filter(api_allowed=True) if x.googlecreds]

    def tempToGoogle(temp_file, uploader):
        assert isinstance(temp_file, TempLocalFile)
        assert isinstance(uploader, Profile)
        return GoogleFile.InitializeTempFile(temp_file, uploader)

    def googleToTemp(google_file):
        assert isinstance(google_file, GoogleFile)
        return google_file.download_and_delete()


    time.sleep(1)
    profile_generator = AuthorizedProfileGenerator()
    while True:
        time.sleep(1)
        for profile in profile_generator:
            if not profile:
                time.sleep(120)
                print("No profiles found!")
            
            for local in TempLocalFile.objects.all():
                try:
                    tempToGoogle(local, profile)
                except:
                    time.sleep(30)
                    break
                print("{} uploaded".format(local))


def StorageSystemLoop():
    from threading import Thread
    from time import sleep
    from main.storage import StorageSystem
    print("STARTING STORAGE SYSTEM")
    thread = Thread(target = StorageSystem)
    thread.start()

