#!/usr/bin/env python
import hashlib
import argparse
import base64

def main(encode,content,file):
    try:
        while True:
            if encode=="base64" and type(content)==str:
                byteContent=content.encode('utf-8')
                value=(base64.b64encode(byteContent))
                print(value)
                break
                #base64加密
            
            if type(encode)==str and type(content)==str and encode!='base64':
                if encode == "md5":
                    _hash = hashlib.md5()#创建md5对象
                    #md5加密
                if encode == "sha1":
                    _hash = hashlib.sha1()#创建sha1对象
                    #sha1加密
                if encode == "sha256":
                    _hash = hashlib.sha256()#创建sha256对象
                    #sha256加密
                if encode == "sha512":
                    _hash = hashlib.sha512()#创建sha512对象
                    #sha512加密
                
                _hash.update(str.encode(content))#更新哈希内容
                value = _hash.hexdigest()#获取哈希值(返回哈希值十六进制字符串)
                print(value)
                break
            
            else:
                print("usage: encrypt.py [-h] [-e E] [-s S] [-f F]")
                print("input encrypt.py -h to ask help")
                break
                #帮助
            
        if type(file)==str:
                with open(file,'w+',encoding='utf-8') as f:
                    f.write(str(value))
                #写入文件
            
    except BaseException as e:
        print(e)
    ##哈希加密
        
if __name__ == "__main__":
    parser=argparse.ArgumentParser()#构建参数解释器
    
    parser.add_argument('-e',help='Specified encoding type ( base64, md5, sha1, sha256, sha512)')
    parser.add_argument('-s',help='Specified content(string)')
    parser.add_argument('-f',help='Generate a file and save hash value')
    args=parser.parse_args()
    #添加传参关键词并解析参数
    main(args.e,args.s,args.f)
