class NoCredsFound(Exception):
    
    def __init__(self, context: str):
        self.context = context

    def __str__(self) -> str:
        return f"Could not find required environment variables: {self.context}"
