import threading
from api import startApi


threading.Thread(target=startApi).start()
