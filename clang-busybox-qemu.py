import os,sys,glob
import getpass
import subprocess
from subprocess import Popen,PIPE
import pathlib
import requests,bs4
import re
import tarfile

filename_links_kernel='links_kernel'
filename_links_busybox='links_busybox'
HOME=os.environ.get('HOME')
PATH=os.environ.get('PATH')
STAGE=HOME + "/tla"
TC_DIR=STAGE + "/tc_dir"
TOP=STAGE + "/teeny-linux"
HELPER_DIR=STAGE + "/helper_dir"


# used for busybox
check_bb=[]



def launch_qemu():
    os.system("export PATH="+ HELPER_DIR + '/' + '/qemu-arm-binaries/' + ':' + '$PATH' + ';'  + "qemu-system-aarch64 -M virt -cpu cortex-a53  -kernel " +TOP +"/obj/kernel-build/arch/arm64/boot/Image" + ' ' + "-initrd " +TOP+ "/initramfs/initramfs.igz" + ' ' + "-nographic -append " + " \"earlyprintk=serial,ttyS0 rdinit=/sbin/init\"" )


def config_kernel_minimal_compile():
    os.chdir(STAGE)
    kd=glob.glob('linux-*')
    for i in kd:
        if not "tar" in i:
            kernel_dir=i
    os.chdir(kernel_dir)
    os.system("mkdir -pv " + TOP + "/obj/kernel-build/")
    os.system("cp " + HELPER_DIR + "/qemu-arm-binaries/defconfig" + ' ' + TOP + "/obj/kernel-build/.config")
    os.system("source " + TC_DIR + "/sdk/clang_sdk/environment-setup-cortexa57-poky-linux-musl" + ';'+ "make " + " ARCH=arm64" + " CROSS_COMPILE=aarch64-poky-linux-musl- " + " CC=\"$CLANGCC\"" + " O=" + TOP+"/obj/kernel-build" + " olddefconfig" )
    os.system("source " + TC_DIR + "/sdk/clang_sdk/environment-setup-cortexa57-poky-linux-musl" + ';'+ "make -j8" + " ARCH=arm64" + " CROSS_COMPILE=aarch64-poky-linux-musl- " + " CC=\"$CLANGCC\"" + " O=" + TOP+"/obj/kernel-build" )



def create_initramfs():
    busybox_init=TOP+'/initramfs/arm-busybox'
    os.chdir(busybox_init)
    os.system("find . | cpio -H newc -o > ../initramfs.cpio;cd ..;cat initramfs.cpio | gzip > initramfs.igz")

def create_init_file():
    os.system("touch " + TOP + '/initramfs/arm-busybox/etc/inittab')
    os.system(" echo ::sysinit:/etc/init.d/rcS >> " + TOP + '/initramfs/arm-busybox/etc/inittab'+';'+"echo ::askfirst:-/bin/sh >> " + TOP + '/initramfs/arm-busybox/etc/inittab')
    
    os.system("mkdir -p " + TOP + '/initramfs/arm-busybox/etc/init.d')
    os.system("touch " + TOP + '/initramfs/arm-busybox/etc/init.d/rcS')
    os.system("echo '#!/bin/sh' >> " + TOP + '/initramfs/arm-busybox/etc/init.d/rcS'+';'+ "echo 'mount -t proc proc /proc' >> " + TOP + '/initramfs/arm-busybox/etc/init.d/rcS'+';' + "echo 'mount -t sysfs none /sys' >> " + TOP + '/initramfs/arm-busybox/etc/init.d/rcS')
    os.system("chmod +x " + TOP + '/initramfs/arm-busybox/etc/init.d/rcS')


def build_initramfs():
    os.system("mkdir -pv " + TOP + '/initramfs/arm-busybox')
    busybox_init=TOP+'/initramfs/arm-busybox'
    os.chdir(busybox_init)
    os.system("mkdir -pv {bin,dev,sbin,etc,proc,sys/kernel/debug,usr/{bin,sbin},lib,lib64,mnt/root,root}")
    os.system("cp -av " + TOP+'/obj/busybox-arm64/_install/* ' + ' ' + TOP +"/initramfs/arm-busybox")
    


def minimal_userland():
    os.chdir(STAGE)
    os.system("busybox_dir=`ls -d */ | grep busybox`;cd $busybox_dir; pwd ;" + "mkdir -pv " + TOP + '/obj/busybox-arm64')
    os.system("cp " + HELPER_DIR + "/qemu-arm-binaries/busybox-yocto-clang.patch " + STAGE )
    os.system("cp " + HELPER_DIR + "/qemu-arm-binaries/0001-Turn-ptr_to_globals-and-bb_errno-to-be-non-const.patch " + STAGE )
    os.system("busybox_dir=`ls -d */ | grep busybox`;cd $busybox_dir; patch -p1 < ../busybox-yocto-clang.patch;patch -p1 < ../0001-Turn-ptr_to_globals-and-bb_errno-to-be-non-const.patch")
    os.system("busybox_dir=`ls -d */ | grep busybox`;cd $busybox_dir" + ';' + "source " + TC_DIR + '/sdk/clang_sdk/environment-setup-cortexa57-poky-linux-musl ' + ';'+ "make O=" + TOP+'/obj/busybox-arm64' + ' ARCH=arm64' + ' CROSS_COMPILE=aarch64-poky-linux-musl- ' + ' CC=\"$CLANGCC\"' + ' defconfig')
    busybox_build=TOP+'/obj/busybox-arm64'
    os.chdir(busybox_build)
    os.system("sed -i  's/# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config")
    os.system("source " + TC_DIR + "/sdk/clang_sdk/environment-setup-cortexa57-poky-linux-musl" + ';'+ "make " + " ARCH=arm64" + " CROSS_COMPILE=aarch64-poky-linux-musl- " + " CC=\"$CLANGCC\"" )
    os.system("source " + TC_DIR + "/sdk/clang_sdk/environment-setup-cortexa57-poky-linux-musl" + ';'+ "make " + " ARCH=arm64" + " CROSS_COMPILE=aarch64-poky-linux-musl- " + " CC=\"$CLANGCC\"" + ' install' )



def DownloadKernelBusybox():
        os.chdir(STAGE)
        print('inside download dir \n')
        print(STAGE)
        ker=glob.glob('linux-*')
        if ker:
                print("linux dir exists, skip downloading \n")
        else:
                print("Getting latest Stable Kernel \n")
                res=requests.get('https://www.kernel.org/')
                fo=bs4.BeautifulSoup(res.text,'html.parser')
                check=fo.select('#latest_link')
                for i in check:
                        with open(filename_links_kernel,'w') as fo1:
                                fo1.write(str(i))

                with open(filename_links_kernel) as fo2:
                        for line in fo2:
                                if "href" in line:
                                        y=line.rstrip()
                                        quoted = re.findall(r'"([^"]*)"',y)
                                        latest_kernel=quoted[0]
                                        print(latest_kernel)
                                        get_kernel=requests.get(latest_kernel)
                                        zname = "linux-source.tar.xz"
                                        zfile = open(zname, 'wb')
                                        zfile.write(get_kernel.content)
                                        zfile.close()
                                        k_tar=tarfile.open('linux-source.tar.xz')
                                        k_tar.extractall('.')
                                        k_tar.close()


        bb=glob.glob('busybox-*')
        if bb:
                print("busybox dir exists, skip downloading \n")
        else:
                print("Getting Latest Stable busybox \n")
                res=requests.get('https://www.busybox.net/')
                fob=bs4.BeautifulSoup(res.text,'html.parser')
                checkb=fob.select('li')
                for y in checkb:
                        bb=str(y)
                        if "(stable)" in bb:
                                check_bb.append(bb)
                for i in check_bb[0]:
                        with open(filename_links_busybox,'a') as fob1:
                                fob1.write(str(i))
                with open(filename_links_busybox) as fob2:
                        for line in fob2:
                                if "tar.bz2" in line:
                                        print(line)
                                        y=line.rstrip()
                                        quoted = re.findall(r'"([^"]*)"',y)
                                        latest_busybox=quoted[0]
                                        print(latest_busybox)
                                        get_busybox=requests.get(latest_busybox)
                                        zname = "busybox-source.tar.bz2"
                                        zfile = open(zname, 'wb')
                                        zfile.write(get_busybox.content)
                                        zfile.close()
                                        k_tarb=tarfile.open('busybox-source.tar.bz2')
                                        k_tarb.extractall('.')
                                        k_tarb.close()



def Install_tc():
    os.chdir(TC_DIR)
    os.system("cp " + HELPER_DIR + '/qemu-arm-binaries/clang-musl-sdk.tar.gz ' + '.' + ';'+ "tar xf clang-musl-sdk.tar.gz;cd sdk;" + "cp " + HELPER_DIR + '/qemu-arm-binaries/install-poky-tc-clang ' + '.' + ';' +  './install-poky-tc-clang ')



def DownloadHelper():
        if os.path.isdir(HELPER_DIR):
                print("Helper  dir exists")
        else:
                os.mkdir(HELPER_DIR)
                os.chdir(HELPER_DIR)
                os.system("git clone https://github.com/Anand1985-gl/qemu-arm-binaries.git")


def createWorkArea():
        if os.path.isdir(STAGE):
            print("Stage dir  exists")
        else:
            os.mkdir(STAGE)
        print(STAGE)

        if os.path.isdir(TC_DIR):
                print("Toolchain dir exists")
        else:
                os.mkdir(TC_DIR)

        if os.path.isdir(TOP):
                print("Top dir exsists")
        else:
                os.mkdir(TOP)
        print(TOP)
        print('work space created \n')



if __name__=='__main__':
    print("Creating work Area \n")
    createWorkArea()
    print("Download helper artifacts and clang toolchain \n")
    DownloadHelper()
    print("Install clang toolchain \n")
    Install_tc()
    print("Download kernel and busybox \n")
    DownloadKernelBusybox()
    print("Create minimal userland  busybox \n")
    minimal_userland()
    print("create initramfs structure \n")
    build_initramfs()
    print("create init file \n")
    create_init_file()
    print("crate initramfs tar file \n")
    create_initramfs()
    print("config_kernel_minimal_compile \n")
    config_kernel_minimal_compile()
    print("launching qemu \n")
    launch_qemu()
