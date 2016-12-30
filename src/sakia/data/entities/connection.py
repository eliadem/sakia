import attr
from duniterpy.documents import block_uid, BlockUID
from duniterpy.key import ScryptParams


@attr.s()
class Connection:
    """
    A connection represents a connection to a currency's network
    It is defined by the currency name, and the key informations
    used to connect to it. If the user is using an identity, it is defined here too.
    """
    currency = attr.ib(convert=str)
    pubkey = attr.ib(convert=str)
    salt = attr.ib(convert=str)
    uid = attr.ib(convert=str, default="", cmp=False, hash=False)
    scrypt_N = attr.ib(convert=int, default=4096)
    scrypt_r = attr.ib(convert=int, default=16)
    scrypt_p = attr.ib(convert=int, default=1)
    blockstamp = attr.ib(convert=block_uid, default=BlockUID.empty(), cmp=False, hash=False)
    password = attr.ib(init=False, convert=str, default="", cmp=False, hash=False)

    def title(self):
        return self.uid + "[" + self.pubkey[:7] + "]@" + self.currency

    @property
    def scrypt_params(self):
        return ScryptParams(self.scrypt_N, self.scrypt_r, self.scrypt_p)
