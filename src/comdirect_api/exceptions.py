class ComdirectError(Exception):
    """Base exception for all comdirect API errors."""


class AuthenticationError(ComdirectError):
    pass


class TanError(AuthenticationError):
    pass


class ApiError(ComdirectError):
    def __init__(self, response):
        self.status_code = response.status_code
        self.body = response.text
        super().__init__(f"HTTP {self.status_code}: {self.body}")
