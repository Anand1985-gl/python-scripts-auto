#### crosstool-ng
####


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


##For Bootlin toolchain 
toolchain_link='https://toolchains.bootlin.com'

# used for busybox
check_bb=[]

# used for Bootlin toolchain
all_toolchain=[]




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
    os.system("export PATH="+ TC_DIR + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+  ';'+"make ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu-  O=" +TOP+"/obj/kernel-build olddefconfig")
    os.system("export PATH="+ TC_DIR + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+ ';' + "time make ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu- O=" +TOP+"/obj/kernel-build -j2")





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
    os.system("cp -av " + TOP+'/obj/busybox-arm/_install/* ' + ' ' + TOP +"/initramfs/arm-busybox")





def minimal_userland():
	os.chdir(STAGE)
	busybox=glob.glob('busybox-*')
	print(busybox)
	busybox_dir=busybox[1]
	bd=os.chdir(busybox_dir)
#	os.system("cp " + HELPER_DIR + '/qemu-arm-binaries/busybox-1.31.1-glibc-2.31.patch' + ' ' + '.')
#	os.system("patch -p1 < busybox-1.31.1-glibc-2.31.patch")
	cwd=os.getcwd()
	print(cwd)
	barm="obj/busybox-arm"
	barm_path=os.path.join(TOP,barm)
	print(barm_path)
	os.system("mkdir -p " + barm_path)
	cmd='export PATH='+ TC_DIR + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+ ';'+'make O=' + barm_path + ' ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu- defconfig'
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
		cmd2='export PATH='+ TC_DIR + '/'+ 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+ ';'+ 'make -j2 ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu-'
		bb3=subprocess.run(cmd2,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb3.stdout)
		cmd3='export PATH='+ TC_DIR + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' + ':' + '$PATH'+ ';'+ 'make ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu-  install'
		bb4=subprocess.run(cmd3,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
#		print(bb4.stdout)
		

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
    os.system("cp -r " + HELPER_DIR + '/qemu-arm-binaries/cross-tool-ng/* ' + '.' + ';'+ "cat ctng-t* > ctng-toolchain.tar.gz;tar xf ctng-toolchain.tar.gz;")





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
    print("Creating work area \n")
    createWorkArea()
    print("Download helper artifacts and crosstool-ng toolchain \n")
    DownloadHelper()
    print("Install crosstool-ng toolchain \n")
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
 
