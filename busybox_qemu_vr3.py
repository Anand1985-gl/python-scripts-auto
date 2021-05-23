## Linaro  toolchain
## 
##
##

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
filename_toolchain='toolchain_name'
HOME=os.environ.get('HOME')
PATH=os.environ.get('PATH')
pass_file=HOME + "/password.txt"

check_bb=[]


def 	launchQemu():
	os.system("export PATH="+ HELPER_DIR + '/' + '/qemu-arm-binaries/' + ':' + '$PATH' + ';'  + "qemu-system-aarch64 -M virt -cpu cortex-a53  -kernel " +TOP +"/obj/kernel-build/arch/arm64/boot/Image" + ' ' + "-initrd " +TOP+ "/obj/initramfs.igz" + ' ' + "-nographic -append " + "earlyprintk=serial,ttyS0" )


def	makeKernel():
	os.chdir(STAGE)
	kd=glob.glob('linux-*')
	print(kd)
	kernel_dir=kd[1]
	os.chdir(kernel_dir)
	os.system("export PATH="+ TC_DIR + '/' + tcbd + '/bin' + ':' + '$PATH'+ ';' + "time make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- O=" +TOP+"/obj/kernel-build -j2")


def     config_kernel_minimal():
	os.chdir(STAGE)
	kd=glob.glob('linux-*')
	print(kd)
	kernel_dir=kd[1]
	os.chdir(kernel_dir)
	os.system("mkdir -pv " + TOP + "/obj/kernel-build/")
	os.system("cp " + HELPER_DIR + "/qemu-arm-binaries/defconfig" + ' ' + TOP + "/obj/kernel-build/.config")
	os.system("export PATH="+ TC_DIR + '/' + tcbd + '/bin' + ':' + '$PATH'+ ';'+"make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- O=" +TOP+"/obj/kernel-build olddefconfig")


def	create_initramfs():
	os.chdir(TOP)
	os.chdir("initramfs/arm-busybox")
	os.system("find . | cpio -H newc -o > ../initramfs.cpio")
	os.chdir(TOP)
	os.chdir("initramfs")
	print(os.getcwd())
	os.system("cat initramfs.cpio | gzip > " + TOP + "/obj/initramfs.igz")


def createInitFile():
	init_f="initramfs/arm-busybox/init"
	print(TOP)
	INIT_file=os.path.join(TOP,init_f)
	print(INIT_file)
	print(type(INIT_file))
	with open(INIT_file, 'w') as file_object:
		file_object.write("#!/bin/sh \n")       
		file_object.write("mount -t proc none /proc \n")
		file_object.write("mount -t sysfs none /sys  \n")
		file_object.write("mount -t debugfs none /sys/kernel/debug  \n")
		file_object.write("echo -e \"\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n\"  \n")
		file_object.write("exec /bin/sh")
	os.system("chmod +x " + TOP + "/initramfs/arm-busybox/init")


def createInitramsStructure():
	os.system("mkdir -pv " + TOP + "/initramfs/arm-busybox")
	os.chdir(TOP)
	print(os.getcwd())
	os.chdir("initramfs/arm-busybox")
	os.system("mkdir -pv {bin,dev,sbin,etc,proc,sys/kernel/debug,usr/{bin,sbin},lib,lib64,mnt/root,root}")
	os.system("cp -av " + TOP + "/obj/busybox-arm/_install/*" + ' ' + TOP +"/initramfs/arm-busybox")
	os.system("sleep 5  | cat " + HOME + '/password.txt' + " | sudo -S  cp -av /dev/{null,console,tty} " + ' ' + TOP + "/initramfs/arm-busybox/dev" )


def minimalUserland():
	os.chdir(STAGE)
	busybox=glob.glob('busybox-*')
	print(busybox)
	busybox_dir=busybox[0]
	bd=os.chdir(busybox_dir)
	cwd=os.getcwd()
	print(cwd)
	barm="obj/busybox-arm"
	barm_path=os.path.join(TOP,barm)
	print(barm_path)
	os.system("mkdir -p " + barm_path)
	cmd='export PATH='+ TC_DIR + '/' + tcbd + '/bin' + ':' + '$PATH'+ ';'+'make O=' + barm_path + ' ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig'
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
		cmd2='export PATH='+ TC_DIR + '/'+ tcbd + '/bin' + ':' + '$PATH'+ ';'+ 'make -j2 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-'
		bb3=subprocess.run(cmd2,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
		print(bb3.stdout)
		cmd3='export PATH='+ TC_DIR + '/' + tcbd + '/bin' + ':' + '$PATH'+ ';'+ 'make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-  install'
		bb4=subprocess.run(cmd3,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
		print(bb4.stdout)
		

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


def createWorkArea():
	global HOME
	HOME=os.environ.get('HOME')
	tla='tla'
	global STAGE
	STAGE=os.path.join(HOME,tla)
	if os.path.isdir(STAGE):
		print("Stage dir  exists")
	else:
		os.mkdir(STAGE)
	print(STAGE)

	tc_dir='tc_dir'
	global TC_DIR
	TC_DIR=os.path.join(STAGE,tc_dir)
	if os.path.isdir(TC_DIR):
		print("Toolchain dir exists")
	else:
		os.mkdir(TC_DIR)

	tl='teeny-linux'
	global TOP
	TOP=os.path.join(STAGE,tl)
	if os.path.isdir(TOP):
		print("Top dir exsists")
	else:
		os.mkdir(TOP)
	print(TOP)	
	print('work space created \n')



def DownloadHelper():
	helper_dir='helper_dir'
	global HELPER_DIR
	HELPER_DIR=os.path.join(STAGE,helper_dir)
	if os.path.isdir(HELPER_DIR):
		print("Helper  dir exists")
	else:
		os.mkdir(HELPER_DIR)
		os.chdir(HELPER_DIR)
		os.system("git clone https://github.com/Anand1985-gl/qemu-arm-binaries.git")



def DownloadLinaroToolchain():
	os.chdir(TC_DIR)
	print("Enter  Toolchain dir \n")
	print("getting   aarch64  Linaro toolchain \n")
	
	tcc=glob.glob('gcc-linaro-*')
	if tcc:
		print("toolchain downloaded and extarcted already , skip downloading \n")
		dirname=os.listdir()
		for i in dirname:
			if os.path.isdir(i):
				global tcbd
				tcbd=i
				print(tcbd)
	else:
		res=requests.get('https://www.linaro.org/downloads/')
		fo=bs4.BeautifulSoup(res.text,'html.parser')

		check=fo.find_all(class_="table responsive-table")
		check1=bs4.BeautifulSoup(str(check),'html.parser')
		check2=check1.find_all('a')
	
		for i in check2:
			if "aarch64-linux-gnu" in str(i):
				k=str(i)
				y=k.rstrip()
				quoted = re.findall(r'"([^"]*)"',y)
				toolchain_link=quoted[0]
				res=requests.get(toolchain_link)
				fo1=bs4.BeautifulSoup(res.text,'html.parser')
				tar=fo1.find_all('a')
				for y in tar:
					if not ".asc" in str(y):
						if "x86_64_aarch64-linux-gnu.tar.xz" in str(y):
							with open(filename_toolchain,'a') as fo2:
								fo2.write(str(y))

				with open(filename_toolchain) as fo3:
					for i in fo3:
						if "href" in i:
							qu=re.findall(r'"([^"]*)"',i)
							tar1=qu[0]
							tar2=str.split(tar1,'/')
							tar3=tar2[-1]
							print(tar3)
				global Ft
				Ft=os.path.join(toolchain_link,tar3)
				print(Ft)
				print("Got toolchian path , now downloading aarch64 toolchain \n")
				get_toolchain=requests.get(Ft)
				zname = "toolchain-binaries.tar.xz"
				zfile = open(zname, 'wb')
				zfile.write(get_toolchain.content)
				zfile.close()
				k_tarb=tarfile.open('toolchain-binaries.tar.xz')
				print(type(k_tarb))
				k_tarb.extractall('.')
				k_tarb.close()
				dirname=os.listdir()
				for i in dirname:
					if os.path.isdir(i):
						global tcbd
						tcbd=i
						print(tcbd)	
	


if __name__ =='__main__':
	print("Creating work Area \n")
	createWorkArea()
	print("Downloading cross toolchain from Linaro \n")
	DownloadLinaroToolchain()
	print("Download helper artifacts \n")
	DownloadHelper()
	print('Download kernel and busybox \n')
	DownloadKernelBusybox()
	print('Building Minimal userland \n')
	minimalUserland()
	print('create initramfs structure \n')
	createInitramsStructure()
	print('Create init file and make it exectuble \n')
	createInitFile()
	print("create Initramfs \n")
	create_initramfs()
	print("Config kernel minimal \n")
	config_kernel_minimal()
	print("Make Kernel \n")
	makeKernel()
	print("Launching qemu \n")
	launchQemu()
