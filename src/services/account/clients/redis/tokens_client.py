class TokensClient:
    def __init__(self):
        self._tokens_blacklist = set()
        self._tokes_pairs = {}

    async def connect(self):
        pass

    async def update_tokens_pair(self, access_token: str, refresh_token: str):
        self._tokes_pairs.update({refresh_token: access_token})

    async def _add_access_token_to_blacklist(self, access_token: str):
        self._tokens_blacklist.add(access_token)

    async def _get_access_token(self, refresh_token: str):
        return self._tokes_pairs.get(refresh_token, None)

    async def _remove_tokens_pair(self, refresh_token: str):
        self._tokes_pairs.pop(refresh_token, None)

    async def is_access_token_in_black_list(self, access_token: str):
        return access_token in self._tokens_blacklist

    async def block_old_tokens_pair(self, refresh_token: str):
        old_access_token = await self._get_access_token(refresh_token)
        await self._add_access_token_to_blacklist(old_access_token)
        await self._remove_tokens_pair(refresh_token)

    async def disconnect(self):
        pass

    def __del__(self):
        pass
