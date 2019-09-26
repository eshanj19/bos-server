class ValidationException(Exception):
    def __init__(self, errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(errors)

        # Now for your custom code...
        self.errors = errors

