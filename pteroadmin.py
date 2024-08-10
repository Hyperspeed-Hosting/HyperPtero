from Pythactyl.Admin import PterodactylAdmin
from pydactyl import PterodactylClient

from secret import PTERO_API
from sql import User

class PteroAdmin():
    def __init__(self) -> None:
        self.link = "https://control.hyspeedhosting.com"
        self.api_key = PTERO_API
        self.adminAPI = PterodactylAdmin(self.link, self.api_key)

    def locateUserByEmail(self, email: str) -> int:
        for i, user in enumerate(self.adminAPI.listUsers(), start=1):
            if user.email == email:
                return i+1
        return -1

    def verifyFunctionality(self, api: str) -> bool: 
        '''
        Verify the API functionality
        '''
        try:
            api = PterodactylClient("https://control.hyspeedhosting.com", api)
            my_servers = api.client.servers.list_servers()
            return True #True because it managed to collect data
        except Exception as e:
            print(e)
            return False
        

class PteroClient():
    def __init__(self, api_key, email) -> None:
        self.api_key = api_key
        self.email = email

        self.id = None


    def checkAPI(self, discord_id): #test client's api key
        api = PterodactylClient(url = "https://control.hyspeedhosting.com", api_key=self.api_key)
        my_email = api.client.account.get_account()
        print(my_email['attributes']['email'])
        my_servers = api.client.account.api_key_list()
        for my_api in my_servers:
            if my_api['identifier'] == self.api_key[0:16]:
                return User(discord_id=discord_id,pterodactyl_id=my_email['attributes']['id'], pterodactyl_api_key=self.api_key, user_id=None, email=self.email)            
            continue
        return None
