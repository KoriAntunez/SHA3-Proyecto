import pytest
from hashs.sha3 import *

class TestSHA3:
    def test_sha_224(self):
        assert sha3_224('hello world') == 'dfb7f18c77e928bb56faeb2da27291bd790bc1045cde45f3210bb6c5'

    def test_sha_256(self):
        assert sha3_256('hello world') == '644bcc7e564373040999aac89e7622f3ca71fba1d972fd94a31c3bfbf24e3938'

    def test_sha_384(self):
        assert sha3_384('hello world') == '83bff28dde1b1bf5810071c6643c08e5b05bdb836effd70b403ea8ea0a634dc4997eb1053aa3593f590f9c63630dd90b'

    def test_sha_512(self):
        assert sha3_512('hello world') == '840006653e9ac9e95117a15c915caab81662918e925de9e004f774ff82d7079a40d4d27b1b372657c61d46d470304c88c788b3a4527ad074d1dccbee5dbaa99a'

    def test_shake128(self):
        assert shake128('hello world', 128) == '3a9159f071e4dd1c8c4f968607c30942'

    def test_shake256(self):
        assert shake256('hello world', 256) == '369771bb2cb9d2b04c1d54cca487e372d9f187f73f7ba3f65b95c8ee7798c527'
