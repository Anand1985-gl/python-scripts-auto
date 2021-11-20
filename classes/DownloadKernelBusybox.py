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


filename_links_kernel='links_kernel'
filename_links_busybox='links_busybox'

# used for busybox
check_bb=[]


class DownloadKernelBusybox():
    def __init__(self):
        self.hv=CreateWorkArea()


    def download_kernel_busybox(self):
        os.chdir(self.hv.stage)
        print("inside download dir \n") 
        print(self.hv.stage)
        ker = glob.glob("linux-*")
        if ker:
            print("linux dir exists, skip downloading \n")
        else:
            print("Getting latest Stable Kernel \n")
            res = requests.get("https://www.kernel.org/")
            fo = bs4.BeautifulSoup(res.text, "html.parser")
            check = fo.select("#latest_link")
            for i in check:
                with open(filename_links_kernel, "w") as fo1:
                    fo1.write(str(i))

            with open(filename_links_kernel) as fo2:
                for line in fo2:
                    if "href" in line:
                        y = line.rstrip()
                        quoted = re.findall(r'"([^"]*)"', y)
                        latest_kernel = quoted[0]
                        print(latest_kernel)
                        get_kernel = requests.get(latest_kernel)
                        zname = "linux-source.tar.xz"
                        zfile = open(zname, "wb")
                        zfile.write(get_kernel.content)
                        zfile.close()
                        k_tar = tarfile.open("linux-source.tar.xz")
                        k_tar.extractall(".")
                        k_tar.close()

        bb = glob.glob("busybox-*")
        if bb:
            print("busybox dir exists, skip downloading \n")
        else:
            print("Getting Latest Stable busybox \n")
            res = requests.get("https://www.busybox.net/")
            fob = bs4.BeautifulSoup(res.text, "html.parser")
            checkb = fob.select("li")
            for y in checkb:
                bb = str(y)
                if "(stable)" in bb:
                    check_bb.append(bb)
            for i in check_bb[0]:
                with open(filename_links_busybox, "a") as fob1:
                    fob1.write(str(i))
        with open(filename_links_busybox) as fob2:
            for line in fob2:
                if "tar.bz2" in line:
                    print(line)
                    y = line.rstrip()
                    quoted = re.findall(r'"([^"]*)"', y)
                    latest_busybox = quoted[0]
                    print(latest_busybox)
                    get_busybox = requests.get(latest_busybox)
                    zname = "busybox-source.tar.bz2"
                    zfile = open(zname, "wb")
                    zfile.write(get_busybox.content)
                    zfile.close()
                    k_tarb = tarfile.open("busybox-source.tar.bz2")
                    k_tarb.extractall(".")
                    k_tarb.close()

