from CreateWorkArea import CreateWorkArea
from ToolChain import ToolChain
from DownloadKernelBusybox import  DownloadKernelBusybox
from UserLand import UserLand
from Kernel import Kernel
import os,sys
import argparse



def launch_qemu():
    os.system("export PATH="+ create_wa.helper_dir + '/' + '/qemu-arm-binaries/' + ':' + '$PATH' + ';'  + "qemu-system-aarch64 -M virt -cpu cortex-a53  -kernel " + create_wa.top  +"/obj/kernel-build/arch/arm64/boot/Image" + ' ' + "-initrd " + create_wa.top + "/initramfs/initramfs.igz" + ' ' + "-nographic -append " + " \"earlyprintk=serial,ttyS0 rdinit=/sbin/init\"" )



if __name__=='__main__':
    create_wa=CreateWorkArea()
    create_wa.create_work_area()
    create_wa.download_helper()
    parser=argparse.ArgumentParser()
    parser.add_argument('--toolchain',type=str,required=True)
    args=parser.parse_args()
    
    if args.toolchain == 'yocto':
        print("Downloading yocto toolchain \n")
        dt=ToolChain()
        dt.yocto_toolchain()
        dkb=DownloadKernelBusybox()
        dkb.download_kernel_busybox()
        userland=UserLand()
        userland.minimal_userland_yocto()
        userland.build_initramfs()
        userland.create_init_file()
        userland.create_initramfs()
        kb=Kernel()
        kb.config_kernel_minimal_yocto()
        launch_qemu()   
    elif args.toolchain == 'crosstool-ng':
        print("Downloading crosstool-ng toolchain \n")
        dt=ToolChain()
        dt.croosstool_ng()
        dkb=DownloadKernelBusybox()
        dkb.download_kernel_busybox()
        userland=UserLand()
        userland.minimal_userland_crosstool_ng()
        userland.build_initramfs()
        userland.create_init_file()
        userland.create_initramfs()
        kb=Kernel()
        kb.config_kernel_minimal_crosstool_ng()
        launch_qemu()
    elif args.toolchain == 'bootlin-buildroot':
        print("Downloading bootlin buildroot toolchain \n")
        dt=ToolChain()
        dt.bootlin_buildroot_ng()
    elif args.toolchain == 'linaro':
        print("Downloading linaro toolchain \n")
        dt=ToolChain()
        dt.linaro()
    elif args.toolchain == 'arm-developer':
        print("Downloading arm developer toolchain \n")
        dt=ToolChain()
        dt.arm_developer()
    elif args.toolchain == 'clang-toolchain':
        print("Downloading clang toolchain \n")
        dt=ToolChain()
        dt.clang_toolchain()
    else:
        print(" given Wrong toolchain option \n")
        sys.exit()
