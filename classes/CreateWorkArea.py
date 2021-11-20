import os,sys,glob

HOME=os.environ.get('HOME')
PATH=os.environ.get('PATH')

class CreateWorkArea():
    def __init__(self,stage='/tla'):
        self.stage=HOME + stage
        self.tc_dir=self.stage + '/tc_dir'
        self.top=self.stage + '/teeny-linux'
        self.helper_dir=self.stage+'/helper_dir'


    def create_work_area(self):
        print("Creating work area \n")
        if os.path.isdir(self.stage):
            print("Stage dir  exists")
        else:
            os.mkdir(self.stage)
        print(self.stage)

        if os.path.isdir(self.tc_dir):
                print("Toolchain dir exists")
        else:
                os.mkdir(self.tc_dir)
        print(self.tc_dir)

        if os.path.isdir(self.top):
                print("Top dir exsists")
        else:
                os.mkdir(self.top)
        print(self.top)
        print('work space created \n')



    def download_helper(self):
        if os.path.isdir(self.helper_dir):
                print("Helper  dir exists")
        else:
                os.mkdir(self.helper_dir)
                os.chdir(self.helper_dir)
                os.system("git clone https://github.com/Anand1985-gl/qemu-arm-binaries.git")
