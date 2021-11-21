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


class UserLand():
    def __init__(self):
        self.hv=CreateWorkArea()


    def minimal_userland_crosstool_ng(self):
        os.chdir(self.hv.stage)
        busybox=glob.glob('busybox-*')
        print(busybox)
        busybox_dir=busybox[1]
        bd=os.chdir(busybox_dir)
#	os.system("cp " + HELPER_DIR + '/qemu-arm-binaries/busybox-1.31.1-glibc-2.31.patch' + ' ' + '.')
#	os.system("patch -p1 < busybox-1.31.1-glibc-2.31.patch")
        cwd=os.getcwd()
        print(cwd)
        barm="obj/busybox-arm"
        barm_path=os.path.join(self.hv.top,barm)
        print(barm_path)
        os.system("mkdir -p " + barm_path)
        cmd='export PATH='+ self.hv.tc_dir + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+ ';'+'make O=' + barm_path + ' ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu- defconfig'
        print(cmd)
        bb1=subprocess.run(cmd,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
        print(bb1.stdout)
        rc=bb1.returncode
        if rc!=0:
            print('busybox defconf failed')
        else:
                print('setting defconfig successfull \n')
                print('Building busybox as static \n')
                cmd1='sed -i ' + '\'s/# CONFIG_STATIC is not set/CONFIG_STATIC=y/\' ' + barm_path + "/.config"
                print(cmd1)
                bb2=subprocess.run(cmd1,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
                print(bb2.stdout)
                os.chdir(barm_path)
                cmd2='export PATH='+ self.hv.tc_dir + '/'+ 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+ ';'+ 'make -j2 ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu-'
                bb3=subprocess.run(cmd2,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb3.stdout)
                cmd3='export PATH='+ self.hv.tc_dir + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' + ':' + '$PATH'+ ';'+ 'make ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu-  install'
                bb4=subprocess.run(cmd3,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb4.stdout)



    def minimal_userland_yocto(self):
        os.chdir(self.hv.stage)
        busybox=glob.glob('busybox-*')
        print(busybox)
        for i in busybox:
            if not "tar" in i:
                busybox_dir=i
        bd=os.chdir(busybox_dir)
        os.system("cp " + self.hv.helper_dir + '/qemu-arm-binaries/*.patch' + ' ' + '.')
#        os.system("patch -p1 < busybox-1.31.1-glibc-2.31.patch")
        os.system("patch -p1 < busybox-yocto.patch")
        cwd=os.getcwd()
        print(cwd)
        barm="obj/busybox-arm"
        barm_path=os.path.join(self.hv.top,barm)
        print(barm_path)
        os.system("mkdir -p " + barm_path)
        cmd='source '+ self.hv.tc_dir + '/' + 'poky_sdk/environment-setup-aarch64-poky-linux' + ';' +'make O=' + barm_path + '  defconfig'
        print(cmd)
        bb1=subprocess.run(cmd,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
        print(bb1.stdout)
        rc=bb1.returncode
        if rc!=0:
            print('busybox defconf failed')
        else:
                print('setting defconfig successfull \n')
                print('Building busybox as static \n')
                cmd1='sed -i ' + '\'s/# CONFIG_STATIC is not set/CONFIG_STATIC=y/\' ' + barm_path + "/.config"
                print(cmd1)
                bb2=subprocess.run(cmd1,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
                print(bb2.stdout)
                os.chdir(barm_path)
                cmd2='source '+ self.hv.tc_dir + '/' + 'poky_sdk/environment-setup-aarch64-poky-linux' + ';' + 'make -j2 '
                bb3=subprocess.run(cmd2,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb3.stdout)
                cmd3='source '+ self.hv.tc_dir + '/' + 'poky_sdk/environment-setup-aarch64-poky-linux' + ';'+ 'make  install'
                bb4=subprocess.run(cmd3,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb4.stdout)
    


    def minimal_userland_bootlin(self):
        os.chdir(self.hv.stage)
        busybox=glob.glob('busybox-*')
        print(busybox)
        busybox_dir=busybox[1]
        bd=os.chdir(busybox_dir)
#        os.system("cp " + self.hv.helper_dir + '/qemu-arm-binaries/busybox-1.31.1-glibc-2.31.patch' + ' ' + '.')
#        os.system("patch -p1 < busybox-1.31.1-glibc-2.31.patch")
        cwd=os.getcwd()
        print(cwd)
        barm="obj/busybox-arm"
        barm_path=os.path.join(self.hv.top,barm)
        print(barm_path)
        os.system("mkdir -p " + barm_path)
        cmd='export PATH='+ self.hv.tc_dir + '/' + 'aarch64--glibc--stable-2020.08-1' + '/bin' + ':' + '$PATH'+ ';'+'make O=' + barm_path + ' ARCH=arm64 CROSS_COMPILE=aarch64-buildroot-linux-gnu-  defconfig'
        print(cmd)
        bb1=subprocess.run(cmd,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
        print(bb1.stdout)
        rc=bb1.returncode
        if rc!=0:
                print('busybox defconf failed')
        else:
                print('setting defconfig successfull \n')
                print('Building busybox as static \n')
                cmd1='sed -i ' + '\'s/# CONFIG_STATIC is not set/CONFIG_STATIC=y/\' ' + barm_path + "/.config"
                print(cmd1)
                bb2=subprocess.run(cmd1,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
                print(bb2.stdout)
                os.chdir(barm_path)
                cmd2='export PATH='+ self.hv.tc_dir + '/'+ 'aarch64--glibc--stable-2020.08-1' + '/bin' + ':' + '$PATH'+ ';'+ 'make -j2 ARCH=arm64 CROSS_COMPILE=aarch64-buildroot-linux-gnu-'
                bb3=subprocess.run(cmd2,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb3.stdout)
                cmd3='export PATH='+ self.hv.tc_dir + '/' + 'aarch64--glibc--stable-2020.08-1' + '/bin' + ':' + '$PATH'+ ';'+ 'make ARCH=arm64 CROSS_COMPILE=aarch64-buildroot-linux-gnu-  install'
                bb4=subprocess.run(cmd3,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb4.stdout)




    def create_initramfs(self):
        busybox_init=self.hv.top +'/initramfs/arm-busybox'   
        os.chdir(busybox_init)
        os.system("find . | cpio -H newc -o > ../initramfs.cpio;cd ..;cat initramfs.cpio | gzip > initramfs.igz")

    def create_init_file(self):
        os.system("touch " + self.hv.top + '/initramfs/arm-busybox/etc/inittab')
        os.system(" echo ::sysinit:/etc/init.d/rcS >> " + self.hv.top + '/initramfs/arm-busybox/etc/inittab'+';'+"echo ::askfirst:-/bin/sh >> " + self.hv.top + '/initramfs/arm-busybox/etc/inittab')
    
        os.system("mkdir -p " + self.hv.top + '/initramfs/arm-busybox/etc/init.d')
        os.system("touch " + self.hv.top + '/initramfs/arm-busybox/etc/init.d/rcS')
        os.system("echo '#!/bin/sh' >> " + self.hv.top + '/initramfs/arm-busybox/etc/init.d/rcS'+';'+ "echo 'mount -t proc proc /proc' >> " + self.hv.top + '/initramfs/arm-busybox/etc/init.d/rcS'+';' + "echo 'mount -t sysfs none /sys' >> " + self.hv.top + '/initramfs/arm-busybox/etc/init.d/rcS')
        os.system("chmod +x " + self.hv.top + '/initramfs/arm-busybox/etc/init.d/rcS')


    def build_initramfs(self):
        os.system("mkdir -pv " + self.hv.top + '/initramfs/arm-busybox')
        busybox_init=self.hv.top+'/initramfs/arm-busybox'
        os.chdir(busybox_init)
        os.system("mkdir -pv {bin,dev,sbin,etc,proc,sys/kernel/debug,usr/{bin,sbin},lib,lib64,mnt/root,root}")
        os.system("cp -av " + self.hv.top +'/obj/busybox-arm/_install/* ' + ' ' + self.hv.top +"/initramfs/arm-busybox")






