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


class Kernel():
    def __init__(self):
        self.hv=CreateWorkArea()


    def config_kernel_minimal_yocto(self):
        os.chdir(self.hv.stage)
        kd=glob.glob('linux-*')
        for i in kd:
            if not "tar" in i:
                kernel_dir=i
        os.chdir(kernel_dir)
        os.system("mkdir -pv " + self.hv.top + "/obj/kernel-build/")
        os.system("cp " + self.hv.helper_dir + "/qemu-arm-binaries/defconfig" + ' ' + self.hv.top + "/obj/kernel-build/.config")
        os.system("source "+ self.hv.tc_dir + '/' + 'poky_sdk/environment-setup-aarch64-poky-linux' + ';' + "make ARCH=arm64   O=" +self.hv.top + "/obj/kernel-build olddefconfig")
        os.system("source "+ self.hv.tc_dir + '/' + 'poky_sdk/environment-setup-aarch64-poky-linux' + ';' + "time make ARCH=arm64   O=" + self.hv.top +"/obj/kernel-build -j2")

    def config_kernel_minimal_crosstool_ng(self):
        os.chdir(self.hv.stage)
        kd=glob.glob('linux-*')
        for i in kd:
            if not "tar" in i:
                kernel_dir=i
        os.chdir(kernel_dir)
        os.system("mkdir -pv " + self.hv.top + "/obj/kernel-build/")
        os.system("cp " + self.hv.helper_dir + "/qemu-arm-binaries/defconfig" + ' ' + self.hv.top + "/obj/kernel-build/.config")
        os.system("export PATH="+ self.hv.tc_dir + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+  ';'+"make ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu-  O=" + self.hv.top +"/obj/kernel-build olddefconfig")
        os.system("export PATH="+ self.hv.tc_dir + '/' + 'x-tools/aarch64-unknown-linux-gnu/bin' +  ':' + '$PATH'+ ';' + "time make ARCH=arm64 CROSS_COMPILE=aarch64-unknown-linux-gnu- O=" + self.hv.top +"/obj/kernel-build -j2")


    def config_kernel_minimal_bootlin(self):
        os.chdir(self.hv.stage)
        kd=glob.glob('linux-*')
        for i in kd:
            if not "tar" in i:
                kernel_dir=i
        os.chdir(kernel_dir)
        os.system("mkdir -pv " + self.hv.top + "/obj/kernel-build/")
        os.system("cp " + self.hv.helper_dir + "/qemu-arm-binaries/defconfig" + ' ' + self.hv.top + "/obj/kernel-build/.config")
        os.system("export PATH="+ self.hv.tc_dir + '/' + 'aarch64--glibc--stable-2020.08-1' + '/bin' + ':' + '$PATH'+ ';'+"make ARCH=arm64 CROSS_COMPILE=aarch64-buildroot-linux-gnu-  O=" +self.hv.top+"/obj/kernel-build olddefconfig")
        os.system("export PATH="+ self.hv.tc_dir + '/' + 'aarch64--glibc--stable-2020.08-1' + '/bin' + ':' + '$PATH'+ ';' + "time make ARCH=arm64 CROSS_COMPILE=aarch64-buildroot-linux-gnu-  O=" + self.hv.top + "/obj/kernel-build -j2")
