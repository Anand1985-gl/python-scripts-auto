##
## 
##
##

import os,sys,glob
import getpass
import subprocess
import pathlib
import requests,bs4
import re
import tarfile

filename_links_kernel='links_kernel'
filename_links_busybox='links_busybox'
HOME=os.environ.get('HOME')
pass_file=HOME + "/password.txt"

check_bb=[]


def 	launchQemu():
	os.system("qemu-system-arm -M versatilepb -dtb " +TOP+ "/obj/linux-arm-versatile_defconfig/arch/arm/boot/dts/versatile-pb.dtb" + ' ' + "-kernel " +TOP +"/obj/linux-arm-versatile_defconfig/arch/arm/boot/zImage" + ' ' + "-initrd " +TOP+ "/obj/initramfs.igz" + ' ' + "-nographic -append " + "earlyprintk=serial,ttyS0" )


def	makeKernel():
	os.chdir(STAGE)
	kd=glob.glob('linux-*')
	print(kd)
	kernel_dir=kd[1]
	os.chdir(kernel_dir)

	os.system("make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- O=" +TOP+"/obj/linux-arm-versatile_defconfig -j2")


def     config_kernel_minimal():
	os.chdir(STAGE)
	kd=glob.glob('linux-*')
	print(kd)
	kernel_dir=kd[1]
	os.chdir(kernel_dir)

	os.system("mkdir -pv " + TOP + "/obj/linux-arm-versatile_defconfig")
	os.system("cp arch/arm/configs/versatile_defconfig " + TOP+ "/obj/linux-arm-versatile_defconfig/.config")
	os.system("make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- O=" +TOP+"/obj/linux-arm-versatile_defconfig olddefconfig")
	os.system("sed -i  's/# CONFIG_EARLY_PRINTK is not set/CONFIG_EARLY_PRINTK=y/'" + ' ' +TOP+"/obj/linux-arm-versatile_defconfig/.config")


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
	cmd='make O=' + barm_path + ' ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- defconfig'
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
		cmd2='make -j2 ARCH=arm CROSS_COMPILE=arm-linux-gnueabi-'
		bb3=subprocess.run(cmd2,shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
		print(bb3.stdout)
		cmd3='make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- install'
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
	tl='teeny-linux'
	global TOP
	TOP=os.path.join(STAGE,tl)
	if os.path.isdir(TOP):
		print("Top dir exsists")
	else:
		os.mkdir(TOP)
	print(TOP)	
	print('work space created \n')



def updateAndInstallToolchain():
	print("Running apt get update \n")
	password=getpass.getpass()
	with open(pass_file,'w') as fo:
		fo.write(password)
	update=subprocess.run('cat  ' + HOME + '/password.txt' +' | sudo -S apt-get update | sleep 4',shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
	print(update.stdout)
	rc=update.returncode
	print(rc)
	if rc!=0:
		print('apt-get update failed \n')
	else:
		print('apt-get update passed \n')	
	

	print("Start Installing cross toolchain \n")
	ans=input("Enter Yes|yes to install toolchain :")
	if ans.lower() == 'yes':
		print("Installing toolchain \n")
		tc=subprocess.run('cat  ' + HOME + '/password.txt' + ' | sudo apt-get install curl libncurses5-dev qemu-system-arm gcc-arm-linux-gnueabi -y',shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
		tu=tc.stdout
		print(tu)	
		rct=tc.returncode
		print(rct)
		if rct!=0:
			print('toolchain installation failed')
		else:
			print('toolchain install success')
	else:
		print('exiting toolchain installation \n')


if __name__ =='__main__':
	print("Running apt-get update and installing cross toolchain \n")
	updateAndInstallToolchain()
	print("Creating work Area \n")
	createWorkArea()
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
