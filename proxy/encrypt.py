# -*- coding:utf-8 -*-
__author__ = 'fremcode@gmail.com'

import sys
import rsa
import base64


class StringEncrypt():
    def __init__(self):
        pass

    def initkey(self):
        (public_key, private_key) = rsa.newkeys(512)
        public = public_key.save_pkcs1()
        public_file = open('public.pem', 'w+')
        public_file.write(public)
        public_file.close()

        private = private_key.save_pkcs1()
        private_file = open('private.pem', 'w+')
        private_file.write(private)
        private_file.close()

    def encrypt(self, de_string, public_file):
        with open(public_file) as fp:
            p = fp.read()
            public_key = rsa.PublicKey.load_pkcs1(p)
            en_tmp = rsa.encrypt(de_string, public_key)
            en_string = base64.encodestring(en_tmp)
            return en_string

    def decrypt(self, en_string, private_file):
        with open(private_file) as fp:
            p = fp.read()
            private_key = rsa.PrivateKey.load_pkcs1(p)
            de_tmp = base64.decodestring(en_string)
            de_string = rsa.decrypt(de_tmp, private_key)
            return de_string

if __name__ == '__main__':
    if not sys.argv[1]:
        print 'use en to encrypt,use de to decrypt!'
        exit()
    if not sys.argv[2]:
        print 'arg 2 is string to encrypt or decrypt!'
        exit()
    action = sys.argv[1]
    string = sys.argv[2]
    encrypt = StringEncrypt()
    if action == 'en':
        enString = encrypt.encrypt(string, 'public.pem')
        print enString
    elif action == 'de':
        deString = encrypt.decrypt(string, 'private.pem')
        print deString
    elif action == 'init':
        encrypt.initkey()
        print 'Create new RSA public,private key success!'
    else:
        print 'use en to encrypt,use de to decrypt!'
