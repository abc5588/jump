from ..hands import *
from .base import BaseService

__all__ = ['DaphneService']


class DaphneService(BaseService):

    def __init__(self):
        super().__init__(name=self.Services.daphne.value)

    @property
    def cmd(self):
        print("\n- Start Daphne ASGI WS Server")

        cmd = [
            'daphne', 'jumpserver.asgi:application',
            '-b', HTTP_HOST,
            '-p', str(WS_PORT),
        ]
        return cmd

    @property
    def cwd(self):
        return APPS_DIR
