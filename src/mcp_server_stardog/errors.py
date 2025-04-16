class StardogClientError(Exception):
    """Custom exception for StardogClient errors."""

    def __init__(
        self,
        message: str,
        url: str,
        status_code: int | None = None,
        details: str | None = None,
    ):
        full_message = f"{message} (URL: {url})"
        if status_code:
            full_message += f" [Status Code: {status_code}]"
        if details:
            full_message += f" Details: {details}"

        super().__init__(full_message)
        self.url = url
        self.status_code = status_code
        self.details = details


class ToolError(Exception):
    """
    Custom exception for tool-related errors.
    """

    def __init__(self, name: str, message: str):
        self.name = name
        error_message = f"Error executing tool: {name} - {message}"
        super().__init__(error_message)


class PromptError(Exception):
    """
    Custom exception for prompt-related errors.
    """

    def __init__(self, name: str, message: str):
        self.name = name
        error_message = f"Error generating prompt: {name} - {message}"
        super().__init__(error_message)
