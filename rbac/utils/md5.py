import hashlib


def gen_md5(origin):
    """
    密码加密
    :param origin:
    :return:
    """
    ha = hashlib.md5(b'ksjdfkjsldf')
    ha.update(origin.encode('utf-8'))
    return ha.hexdigest()
