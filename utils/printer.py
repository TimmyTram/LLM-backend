class bcolors:
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def color_print(colors, msg):
        print(colors + msg + bcolors.ENDC)


    @staticmethod
    def streamPrint(stream, colors=''):
        if colors == '':
            for out in stream:
                print(out, sep=' ', end='', flush=True)
        else:
            for out in stream:
                print(colors + out + bcolors.ENDC, sep=' ', end='', flush=True)