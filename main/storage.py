

def StorageSystem(testRun=False):
    import time
    import shutil

    from main.models import Profile, TempLocalFile, GoogleFile

    def sleepIfNotTest(seconds):
        time.sleep(seconds * (not(testRun)))

    def getFreeSpaceMB():
        return shutil.disk_usage(__file__)[-1] * 0.000001

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

        def refreshProfiles(self):
            self.profiles = [x for x in Profile.objects.filter(api_allowed=True) if x.googlecreds]

    def tempToGoogle(temp_file, uploader):
        assert isinstance(temp_file, TempLocalFile)
        assert isinstance(uploader, Profile)
        return GoogleFile.InitializeTempFile(temp_file, uploader)

    def googleToTemp(google_file):
        assert isinstance(google_file, GoogleFile)
        return google_file.download_and_delete()

    def downloadFiles():
        unauthroized_file_holders = [x for x in Profile.objects.filter(api_allowed=False) if x.unauthorized_file_holder]
        MAX_MB_SIZE_FILE = 10 
        if not unauthroized_file_holders:
            return True # Complete
        print("{} profiles are unauthorized file holders".format(len(unauthroized_file_holders)))
        for profile in unauthroized_file_holders:
            try:
                profile.googlecreds.getDrive()
            except:
                print("{} has terminated drive access, yet still hosts {} files".format(profile, GoogleFile.objects.filter(owned_by=profile).count()))
            
            for file in GoogleFile.objects.filter(owned_by=profile):
                if getFreeSpaceMB() > MAX_MB_SIZE_FILE:
                    googleToTemp(file)
        return True


    def googleToTemp(google_file):
        assert isinstance(google_file, GoogleFile)
        return google_file.download_and_delete()

    sleepIfNotTest(1)
    profile_generator = AuthorizedProfileGenerator(10)
    while True:
        sleepIfNotTest(1)
        if not testRun:
            downloadFiles()
        for profile in profile_generator:
            if not profile:
                sleepIfNotTest(120)
            
            print("Files to upload:", TempLocalFile.objects.all().count())
            for local in TempLocalFile.objects.all():
                try:
                    if not testRun:
                        tempToGoogle(local, profile)
                except Exception as e:
                    print("Upload error:", e)
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

