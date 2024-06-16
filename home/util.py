#status success info warning error

class Notification:
    def __init__(self, title="", content="", status="info"):
        self.title = title
        self.content = content
        self.status = status

