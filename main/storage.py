

def StorageSystem(testRun=False):
    import time
    from main.models import Profile, TempLocalFile, GoogleFile

    def sleepIfNotTest(seconds):
        time.sleep(seconds * (not(testRun)))

    class AuthorizedProfileGenerator():
        def __init__(self, REFRESH_PER_X_CALLS):
            self.refreshProfiles()
            self.REFRESH_PER_X_CALLS = REFRESH_PER_X_CALLS
            self.count_to_refresh = REFRESH_PER_X_CALLS
            
        def __iter__(self):
            if self.count_to_refresh <= 0:
                self.refreshProfiles()
                self.count_to_refresh = self.REFRESH_PER_X_CALLS
            else:
                self.count_to_refresh -= 1

            for profile in self.profiles:
                yield profile

            yield None

        def refreshProfiles(self):
            self.profiles = [x for x in Profile.objects.filter(api_allowed=True) if x.googlecreds]

    def tempToGoogle(temp_file, uploader):
        assert isinstance(temp_file, TempLocalFile)
        assert isinstance(uploader, Profile)
        return GoogleFile.InitializeTempFile(temp_file, uploader)

    def googleToTemp(google_file):
        assert isinstance(google_file, GoogleFile)
        return google_file.download_and_delete()

    sleepIfNotTest(1)
    profile_generator = AuthorizedProfileGenerator(10)
    while True:
        sleepIfNotTest(1)
        for profile in profile_generator:
            if not profile:
                sleepIfNotTest(120)
            
            for local in TempLocalFile.objects.all():
                try:
                    if not testRun:
                        tempToGoogle(local, profile)
                except:
                    sleepIfNotTest(30)
                    break

        if testRun:
            return True



def StorageSystemLoop():
    from threading import Thread
    from time import sleep
    from main.storage import StorageSystem
    try:
        if StorageSystem(True):
            print("Starting storage system")
            thread = Thread(target = StorageSystem)
            thread.start()
        else:
            raise Exception("Did not return True")
    except Exception as e:
        print("STORAGE SYSTEM NOT WORKING:", e)

