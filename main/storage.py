

class AuthorizedProfileGenerator:
    def __init__(self, REFRESH_PER_X_CALLS):
        self.refreshProfiles()
        self.REFRESH_PER_X_CALLS = REFRESH_PER_X_CALLS
        self.count_to_refresh = REFRESH_PER_X_CALLS
        self.loop_index = -1
        
    # def __iter__(self):
    #     from main.models import Profile
    #     while True:
    #         if self.count_to_refresh <= 0:
    #             self.refreshProfiles()
    #             self.count_to_refresh = self.REFRESH_PER_X_CALLS
    #         else:
    #             self.count_to_refresh -= 1

    #         for profile in self.profiles:
    #             yield profile

    #         if not self.profiles:
    #             yield None
    def __iter__(self):
        return self

    def __next__(self):
        from main.models import Profile
        self.loop_index += 1
        # print("CHOICES:", self.profiles)
        # print("INDEX:", self.loop_index)
        try:
            return self.profiles[self.loop_index]
        except:
            self.count_to_refresh -= 1
            self.loop_index = 0

            if self.count_to_refresh <= 0:
                self.refreshProfiles()
                self.count_to_refresh = self.REFRESH_PER_X_CALLS
            
            if not self.profiles:
                return None
            return self.profiles[self.loop_index]


    def refreshProfiles(self):
        from main.models import Profile
        self.profiles = [x for x in Profile.objects.filter(api_allowed=True) if x.has_creds]


def getFreeSpaceMB():
    import shutil

    return shutil.disk_usage(__file__)[-1] * 0.000001


def tempToGoogle(temp_file, uploader):
    from main.models import Profile, TempLocalFile, GoogleFile

    assert isinstance(temp_file, TempLocalFile)
    assert isinstance(uploader, Profile)

    return GoogleFile.InitializeTempFile(temp_file, uploader)

def googleToTemp(google_file):
    from main.models import GoogleFile

    assert isinstance(google_file, GoogleFile)

    return google_file.download_and_delete()

def downloadFiles():
    from main.models import Profile

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


def StorageSystem(testRun=False):
    from main.models import Profile, TempLocalFile, GoogleFile

    import time

    sleepIfNotTest = lambda seconds: time.sleep(seconds * (not(testRun)))

        

    sleepIfNotTest(1)
    profile_generator = AuthorizedProfileGenerator(10)
    while True:
        sleepIfNotTest(1)
        if not testRun:
            downloadFiles()
        to_upload = TempLocalFile.objects.all()
        print("Files to upload:", to_upload.count())
        for file in to_upload:
            profile = next(profile_generator)
            print("Picked profile:", profile)
            if not profile:
                print("No Google Drive to upload files to")
                sleepIfNotTest(120)
                profile_generator.refreshProfiles()
            if not testRun:
                try:
                    tempToGoogle(file, profile)
                except Exception as e:
                    print("Upload error:", e)
                    sleepIfNotTest(30)
                    continue
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

