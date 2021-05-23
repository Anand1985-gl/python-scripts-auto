import os,sys,glob
import getpass
import subprocess
from subprocess import Popen,PIPE
import pathlib
import requests,bs4
import re
import tarfile

HOME=os.environ.get('HOME')
PATH=os.environ.get('PATH')
CLFS=HOME + "/clfs"
SOURCES=CLFS + "/sources"
CLFS_env=CLFS + "/clfs-env"


def run_qemu():
    os.system("source " + CLFS_env + ';'+"export PATH="+ CLFS  + '/qemu-arm-binaries/' + ':' + '$PATH' + ';'+"qemu-system-aarch64 -M virt -cpu cortex-a53  -kernel $HOME/clfs/sources/linux-5.4/arch/arm64/boot/Image -initrd $HOME/clfs/initramfs.igz -nographic -append \"earlyprintk=serial,ttyS0 rdinit=/sbin/init\" ")


def prepare_init_and_ramfs():
    os.chdir(CLFS)
    os.system("source " + CLFS_env + ';' + " touch $HOME/clfs/targetfs/etc/inittab; echo ::sysinit:/etc/init.d/rcS >> $HOME/clfs/targetfs/etc/inittab;echo ::askfirst:-/bin/sh >>  $HOME/clfs/targetfs/etc/inittab")
   
    os.system("source " + CLFS_env + ';' + "mkdir -p $HOME/clfs/targetfs/etc/init.d;touch $HOME/clfs/targetfs/etc/init.d/rcS")
    TARGET_FS=CLFS + "/targetfs"
    RCS=TARGET_FS+"/etc/init.d/rcS"
    with open(RCS, 'w') as file_object:
                file_object.write("#!/bin/sh \n")
                file_object.write("mount -t proc none /proc \n")
                file_object.write("mount -t sysfs none /sys  \n")

   
    os.system("source " + CLFS_env + ';' + "chmod +x $HOME/clfs/targetfs/etc/init.d/rcS")

    os.chdir(TARGET_FS)
    os.system("source " + CLFS_env + ';' + "find . | cpio -H newc -o > ../initramfs.cpio;cd ..;cat initramfs.cpio | gzip > initramfs.igz")


def linux_compile():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+"rm -rf linux-5.4;tar xf linux-5.4.tar.xz;cd linux-5.4;make mrproper;cp $CLFS/qemu-arm-binaries/defconfig $CLFS/sources/linux-5.4/.config;make ARCH=${CLFS_ARCH} CROSS_COMPILE=${CLFS_TARGET}- olddefconfig;make ARCH=${CLFS_ARCH} CROSS_COMPILE=${CLFS_TARGET}-;make ARCH=${CLFS_ARCH} CROSS_COMPILE=${CLFS_TARGET}- INSTALL_MOD_PATH=${CLFS}/targetfs modules_install")


def helper_scripts():
    os.chdir(CLFS)
    os.system("git clone https://github.com/Anand1985-gl/qemu-arm-binaries")


def busybox_install():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+"rm -rf busybox-1.31;tar xf busybox-1.31.1.tar.bz2;cd busybox-1.31.1;make distclean;make ARCH=\${CLFS_ARCH} defconfig;make ARCH=${CLFS_ARCH} CROSS_COMPILE=${CLFS_TARGET}-;make ARCH=${CLFS_ARCH} CROSS_COMPILE=${CLFS_TARGET}- CONFIG_PREFIX=${CLFS}/targetfs install;cp -v examples/depmod.pl ${CLFS}/cross-tools/bin;chmod -v 755 ${CLFS}/cross-tools/bin/depmod.pl")
   


def musl_shared():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+ "rm -rf musl-1.2.0;tar xf musl-1.2.0.tar.gz;cd musl-1.2.0;./configure  CROSS_COMPILE=${CLFS_TARGET}- --prefix=/ --disable-static --target=${CLFS_TARGET} ;make;DESTDIR=${CLFS}/targetfs make install-libs")


def install_libgcc():
    os.system("source " + CLFS_env + ';'+ "cp -v ${CLFS}/cross-tools/${CLFS_TARGET}/lib64/libgcc_s.so.1 ${CLFS}/targetfs/lib/;${CLFS_TARGET}-strip ${CLFS}/targetfs/lib/libgcc_s.so.1")

def target_system():
    os.system("source " + CLFS_env + ';'+ "mkdir -pv ${CLFS}/targetfs")
    os.system("source " + CLFS_env + ';'+ "echo export CC=${CLFS_TARGET}-gcc --sysroot=${CLFS}/targetfs" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export CXX=${CLFS_TARGET}-g++ --sysroot=${CLFS}/targetfs" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export AR=${CLFS_TARGET}-ar" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export AS=${CLFS_TARGET}-as" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export LD=${CLFS_TARGET}-ld --sysroot=${CLFS}/targetfs" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export RANLIB=${CLFS_TARGET}-ranlib" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export READELF=${CLFS_TARGET}-readelf" + '>>' + CLFS_env)
    os.system("source " + CLFS_env + ';'+ "echo export STRIP=${CLFS_TARGET}-strip" + '>>' + CLFS_env)


    os.system("source " + CLFS_env + ';'+ "mkdir -pv ${CLFS}/targetfs/{bin,boot,dev,etc,home,lib/{firmware,modules}};mkdir -pv ${CLFS}/targetfs/{mnt,opt,proc,sbin,srv,sys};mkdir -pv ${CLFS}/targetfs/var/{cache,lib,local,lock,log,opt,run,spool};install -dv -m 0750 ${CLFS}/targetfs/root;install -dv -m 1777 ${CLFS}/targetfs/{var/,}tmp;mkdir -pv ${CLFS}/targetfs/usr/{,local/}{bin,include,lib,sbin,share,src}")

def gcc_final():
    os.chdir(SOURCES)
    os.system("rm -rf gcc-build gcc-9.3.0")
    os.system("source " + CLFS_env + ';'+"tar xf mpfr-4.0.2.tar.xz;mv -v mpfr-4.0.2 mpfr;tar xf mpc-1.1.0.tar.gz;mv -v mpc-1.1.0 mpc;tar xf gmp-6.2.0.tar.bz2;mv -v gmp-6.2.0 gmp;tar xf gcc-9.3.0.tar.xz;mv mpfr gcc-9.3.0;mv mpc gcc-9.3.0;mv gmp gcc-9.3.0;mkdir -v gcc-build;cd gcc-build;../gcc-9.3.0/configure --prefix=${CLFS}/cross-tools --build=${CLFS_HOST}  --host=${CLFS_HOST} --target=${CLFS_TARGET} --with-sysroot=${CLFS}/cross-tools/${CLFS_TARGET} --disable-nls --enable-languages=c --enable-c99 --enable-long-long --disable-libmudflap --disable-libsanitizer --disable-multilib --with-mpfr-include=$(pwd)/../gcc-9.3.0/mpfr/src --with-mpfr-lib=$(pwd)/mpfr/src/.libs --with-arch=${CLFS_ARM_ARCH};make;make install")


def musl_install_1():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+ "tar xf musl-1.2.0.tar.gz;cd musl-1.2.0;./configure CROSS_COMPILE=${CLFS_TARGET}- --prefix=/ --target=${CLFS_TARGET} ;make;DESTDIR=${CLFS}/cross-tools/${CLFS_TARGET} make install")

def gcc_stage_1():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+"tar xf mpfr-4.0.2.tar.xz;mv -v mpfr-4.0.2 mpfr;tar xf mpc-1.1.0.tar.gz;mv -v mpc-1.1.0 mpc;tar xf gmp-6.2.0.tar.bz2;mv -v gmp-6.2.0 gmp;tar xf gcc-9.3.0.tar.xz;mv mpfr gcc-9.3.0;mv mpc gcc-9.3.0;mv gmp gcc-9.3.0;mkdir -v gcc-build;cd gcc-build;../gcc-9.3.0/configure --prefix=${CLFS}/cross-tools --build=${CLFS_HOST} --host=${CLFS_HOST} --target=${CLFS_TARGET} --with-sysroot=${CLFS}/cross-tools/${CLFS_TARGET} --disable-nls  --disable-shared --without-headers --with-newlib --disable-decimal-float --disable-libgomp --disable-libmudflap --disable-libsanitizer --disable-libssp --disable-libatomic--disable-libquadmath --disable-threads --enable-languages=c --disable-multilib --with-mpfr-include=$(pwd)/../gcc-9.3.0/mpfr/src --with-mpfr-lib=$(pwd)/mpfr/src/.libs --with-arch=${CLFS_ARM_ARCH};make all-gcc all-target-libgcc;make install-gcc install-target-libgcc")



def cross_binutils():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+ "tar xf binutils-2.34.tar.bz2;cd binutils-2.34;mkdir -v ../binutils-build;cd ../binutils-build;../binutils-2.34/configure -prefix=${CLFS}/cross-tools --target=${CLFS_TARGET} --with-sysroot=${CLFS}/cross-tools/${CLFS_TARGET} --disable-nls --disable-multilib;make configure-host;make;make install")



def linux_headers():
    os.chdir(SOURCES)
    os.system("source " + CLFS_env + ';'+ "tar xf linux-5.4.tar.xz" + ';' + "cd linux-5.4 ;make mrproper;make ARCH=${CLFS_ARCH} headers_check;make ARCH=${CLFS_ARCH} INSTALL_HDR_PATH=${CLFS}/cross-tools/${CLFS_TARGET} headers_install")



def download_sources():
    os.chdir(SOURCES)
    sources_links = ['https://ftp.gnu.org/gnu/binutils/binutils-2.34.tar.bz2','https://ftp.gnu.org/gnu/gcc/gcc-9.3.0/gcc-9.3.0.tar.xz','https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.4.tar.xz','https://ftp.gnu.org/gnu/mpfr/mpfr-4.0.2.tar.xz','https://ftp.gnu.org/pub/gnu/mpc/mpc-1.1.0.tar.gz','https://ftp.gnu.org/gnu/gmp/gmp-6.2.0.tar.bz2','https://www.musl-libc.org/releases/musl-1.2.0.tar.gz','https://www.busybox.net/downloads/busybox-1.31.1.tar.bz2']
    for i in sources_links:
        r=requests.get(i, allow_redirects=True)
        name = i.rsplit('/', 1)[1]
        x = open(name, 'wb')
        x.write(r.content)
        x.close()


def create_crosstools_area():
    print(CLFS_env)
    os.system("source " + CLFS_env + ';'+ "mkdir -p " + CLFS + '/cross-tools/' + '$CLFS_TARGET')
    os.system("source " + CLFS_env + ';'+ "cd ${CLFS}/cross-tools/${CLFS_TARGET}"+';'+'ln -sfv . ${CLFS}/cross-tools/${CLFS_TARGET}/usr')
    

def create_env():
    clfs_env="clfs-env"
    global CLFS_env
    CLFS_env=os.path.join(CLFS,clfs_env)
    print(CLFS_env)
    with open(CLFS_env,'w') as file_object:
        file_object.write("umask 022 \n")
        file_object.write("CLFS=$HOME/clfs \n")
        file_object.write("LC_ALL=POSIX \n")
        file_object.write("PATH=${CLFS}/cross-tools/bin:/bin:/usr/bin \n")
        file_object.write("export CLFS LC_ALL PATH \n")
        file_object.write("unset CFLAGS \n")
        file_object.write("export CLFS_HOST=\"x86_64-cross-linux-gnu\" \n")
        file_object.write("export CLFS_TARGET=\"aarch64-linux-musl\" \n")
        file_object.write("export CLFS_ARCH=\"arm64\" \n")
        file_object.write("export CLFS_ARM_ARCH=\"armv8-a\"\n")


def createWorkArea():
    if os.path.isdir(CLFS):
        print("clfs dir exists \n")
    else:
        os.mkdir(CLFS)
        os.mkdir(SOURCES)
        os.system("chmod 777 " + CLFS)



if __name__ == '__main__':
    print("welcome to CLFS qemu \n")
    print("setting up work area \n")
    createWorkArea()
    print("creating env file \n")
    create_env()
    print("creating crosstolls area \n")
    create_crosstools_area()
    print("Downloading sources \n")
    download_sources()
    print("Linux headers ..... \n")
    linux_headers()
    print("Cross Binutils ... \n")
    cross_binutils()
    print("Gcc stage 1 ... \n")
    gcc_stage_1()
    print("Musl stage 1 ...\n")
    musl_install_1()
    print("GCC  final ... \n")
    gcc_final()
    print("Creating target system ..\n")
    target_system()
    print("copying gcc to target ... \n")
    install_libgcc()
    print("musl shared final ...\n")
    musl_shared()
    print("busybox install...\n")
    busybox_install()
    print("helper scripts ..\n")
    helper_scripts()
    print("Linux compile ...\n")
    linux_compile()
    print("prepare init and ramfs ..\n")
    prepare_init_and_ramfs()
    print("running qemu .............................\n")
    run_qemu()
