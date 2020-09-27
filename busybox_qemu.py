import os,sys,glob
import getpass
import subprocess
import pathlib


pass_file='password.txt'





def 	launchQemu():
	os.system("qemu-system-arm -M versatilepb -dtb " +TOP+ "/obj/linux-arm-versatile_defconfig/arch/arm/boot/dts/versatile-pb.dtb" + ' ' + "-kernel " +TOP +"/obj/linux-arm-versatile_defconfig/arch/arm/boot/zImage" + ' ' + "-initrd " +TOP+ "/obj/initramfs.igz" + ' ' + "-nographic -append " + "earlyprintk=serial,ttyS0" )



def	makeKernel():
	os.chdir(STAGE)
	os.chdir("linux-4.10.6")
	os.system("make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- O=" +TOP+"/obj/linux-arm-versatile_defconfig -j2")




def     config_kernel_minimal():
	os.chdir(STAGE)
	os.chdir("linux-4.10.6")
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
	os.system("sleep 5 | cat /home/anand/python-prac/sep2/password.txt  | sudo -S cp -av /dev/{null,console,tty} " + ' ' + TOP + "/initramfs/arm-busybox/dev" )



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
		print('setting defconfig successfull')
		print('Building busybox as static')
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
	print('inside download dir')
	print(STAGE)
	ker=glob.glob('linux-*')
	if ker:
		print("linux dir exists, skip downloading \n")
	else:
		down_kernel=subprocess.run('curl https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.10.6.tar.xz | tar xJf -',shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
		print(down_kernel.stdout)

	bb=glob.glob('busybox-*')
	if bb:
		print("busybox dir exists, skip downloading \n")
	else:
		down_busybox=subprocess.run('curl https://busybox.net/downloads/busybox-1.26.2.tar.bz2 | tar xjf -',shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)



def createWorkArea():
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
	update=subprocess.run('cat password.txt  | sudo -S apt-get update | sleep 4',shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
	print(update.stdout)
	rc=update.returncode
	print(rc)
	if rc!=0:
		print('apt-get update failed')
	else:
		print('apt-get update passed')	
	

	print("Start Installing cross toolchain \n")
	ans=input("Enter Yes|yes to install toolchain :")
	if ans.lower() == 'yes':
		print("Installing toolchain \n")
		tc=subprocess.run('cat password.txt  | sudo apt-get install curl libncurses5-dev qemu-system-arm gcc-arm-linux-gnueabi -y',shell=True,check=True, stdout=subprocess.PIPE, universal_newlines=True)
		tu=tc.stdout
		print(tu)	
		rct=tc.returncode
		print(rct)
		if rct!=0:
			print('toolchain installation failed')
		else:
			print('toolchain install success')
	else:
		print('exting toolchain installation')



if __name__ =='__main__':
	print("Running apt-get update and installing cross toolchain ")
	updateAndInstallToolchain()
	print("Creating work Area ")
	createWorkArea()
	print('Download kernel and busybox')
	DownloadKernelBusybox()
	print('Building Minimal userland')
	minimalUserland()
	print('create initramfs structure')
	createInitramsStructure()
	print('Create init file and make it exectuble')
	createInitFile()
	print("create Initramfs")
	create_initramfs()
	print("Config kernel minimal")
	config_kernel_minimal()
	print("Make Kernel")
	makeKernel()
	print("Launching qemu ")
	launchQemu()
