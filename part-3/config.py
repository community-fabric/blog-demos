from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings can be specified here or deleted and used as environment variables.
    Example:
        export IPF_TOKEN='afe045a522a947775e47609937eb7eac'

    Then remove the = 'TOKEN' from the variable:
        ipf_secret: str = "dd2e9858a739f7e0819b159a5dcc8df1"
        ipf_instance: str = 'https://172.22.183.134'
        ipf_token: str
    """
    ipf_secret: str = "9b60669e6803fc67b974707fa8c375c2"
    ipf_instance: str = 'https://192.168.1.100:8444'
    ipf_token: str = 'b02cf6128134a08f2f161593476667c'


settings = Settings()
