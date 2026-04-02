class ProfileNotFoundException(Exception):
    def __init__(self, message="User profile not found"):
        self.message = message
        super().__init__(self.message)
