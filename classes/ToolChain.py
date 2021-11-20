import os,sys,glob
import getpass
import subprocess
from subprocess import Popen,PIPE
import pathlib
import requests,bs4
import re
import tarfile


from CreateWorkArea import CreateWorkArea

HOME=os.environ.get('HOME')
PATH=os.environ.get('PATH')

#yocto link
toolchain_link='http://downloads.yoctoproject.org/releases/yocto/yocto-2.6/toolchain/x86_64/'
all_toolchain=[]


class ToolChain():
    def __init__(self):
        self.hv=CreateWorkArea()



    def croosstool_ng(self):
        os.chdir(self.hv.tc_dir)
        os.system("cp -r " + self.hv.helper_dir + '/qemu-arm-binaries/cross-tool-ng/* ' + '.' + ';'+ "cat ctng-t* > ctng-toolchain.tar.gz;tar xf ctng-toolchain.tar.gz;")

    def yocto_toolchain(self):
        os.chdir(self.hv.tc_dir)
        print("Enter  Toolchain dir \n")
        print("getting   aarch64  Yocto toolchain \n")
	
        tcc=glob.glob('toolchain-binaries*')
        if tcc:
                print("toolchain  downloaded , check if extracted  \n")
                tcc2=glob.glob('poky_sdk*')
                if tcc2:
                        print("toolchain is  extracted \n")
                        dirname=os.listdir() 		
                        for i in dirname:
                            if os.path.isdir(i):
                                        global tcbd
                                        tcbd=i
                                        print(tcbd)
                else:
                        os.system("chmod +x  toolchain-binaries.sh")
                        os.system("cp " + self.hv.helper_dir + '/qemu-arm-binaries/install-poky-tc' + ' ' + '.')
                        os.system("./install-poky-tc")
                        os.system("cp " + self.hv.helper_dir + '/qemu-arm-binaries/crypt.h' + ' ' + self.hv.tc_dir + '/poky_sdk/tmp/sysroots/qemuarm64/usr/include/') 

        else:
                res=requests.get('http://downloads.yoctoproject.org/releases/yocto/yocto-2.6/toolchain/x86_64/')
                fo=bs4.BeautifulSoup(res.text,'html.parser')
                check=fo.find_all('a')
	
                for i in check:
                        tcc=re.compile(r'poky-glibc-x86_64-core-image-minimal-aarch64-toolchain-ext-(\d).(\d).sh')
                        tcc1=tcc.search(str(i))
                        if tcc1:
                            all_toolchain.append(i)

                x=all_toolchain[0]
                qu=re.findall(r'"([^"]*)"',str(x))
                tar1=qu[0]

                global Ft
                Ft=toolchain_link+tar1
                print(Ft)
                print("Got toolchian path , now downloading aarch64 toolchain \n")
                get_toolchain=requests.get(Ft)
                zname = "toolchain-binaries.sh"
                zfile = open(zname, 'wb')
                zfile.write(get_toolchain.content)
                zfile.close()
                os.system("chmod +x  toolchain-binaries.sh")
                os.system("cp " + self.hv.helper_dir + '/qemu-arm-binaries/install-poky-tc' + ' ' + '.')
                os.system("./install-poky-tc")
                os.system("cp " + self.hv.helper_dir + '/qemu-arm-binaries/crypt.h' + ' ' + self.hv.tc_dir + '/poky_sdk/tmp/sysroots/qemuarm64/usr/include/')   
                dirname=os.listdir()
                for i in dirname:
                    if os.path.isdir(i):
                                tcbd=i
                                print(tcbd)   
