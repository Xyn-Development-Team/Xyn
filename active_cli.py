class about:
    version="0.2.2 alpha"
    developers=["ZackTheKill3r","Nyx_Chan0_0"]
    description="A little tool to make the visual part of creating CLI's a piece of cake"
    
import multiprocessing
from termcolor import colored
import ctypes
from time import sleep
import os
import sys

class colors:
    rainbow = ["red","green","yellow","green","cyan","magenta"]
    red = "red"
    grey = "grey"
    green = "green"
    yellow = "yellow"
    blue = "blue"
    magenta = "magenta"
    cyan = "cyan"
    white = "white"

class CLI:
    color_support = True
    "A Quick switch to enable/disable color support"

def pcolor(str,color="white",breakline=True):
    """Use this to print text with colors:\n
    grey, red, green, yellow, blue, magenta, cyan, rainbow and white(default)\n
    You can use replace print by pcolor using: ``from active_cli import pcolor as print``"""
    if CLI.color_support == False : color="white" 
    if color == "rainbow":
        i = 0
        while i < len(str):
            color = colors.rainbow[i % len(colors.rainbow)]
            print(colored(str[i],color),end="")
            i += 1
        return
    if breakline == False: 
        return print(colored(str,color),end="")
    else:
        return print(colored(str,color),end="\n")
    
def divider(size,color="white",print=True):
    """Returns a divider with the specified lenght"""
    if CLI.color_support == False : color="white"
    divider_queue = "█"
    for s in range(size):
        divider_queue = divider_queue + "█"
    if print:
        pcolor(divider_queue,color)
    else:
        return divider_queue

def popup(title,text,type=0):
    """Only works for Windows!\n
    Types = 0 : OK | 1: OK, Cancel | 2: Abort, Retry, Ignore | 3: Yes, No, Cancel | 4: Yes, No | 5: Retry, Cancel | 6: Cancel, Try Again, Continue\n
    User interaction will return values: ok | cancel | abort | yes | no"""
    msgbox = ctypes.windll.user32.MessageBoxW(0, text, title, type)
    if msgbox == 1:
        return "ok"
    elif msgbox == 2:
        return "cancel"
    elif msgbox == 3:
        return "abort"
    elif msgbox == 6:
        return "yes"
    elif msgbox == 7:
        return "no"
    elif msgbox == None or "None":
        return "Ignore/Repeat"

def breakline(lines=1):
    """Break a few lines without actually using pcolor/print"""
    for l in range(lines):
        pcolor("")

def header(size,text,color="white",text_color="white"):
    """Quickly prints a text between two dividers with the specified length and color"""
    if CLI.color_support == False : color="white" ; text_color="white" 
    pcolor(divider(size,print=False),color,breakline=False) ; pcolor(f" {text} ",text_color if text_color != "" else text_color,breakline=False) ; pcolor(divider(size,print=False),color)

def clearconsole():
    os.system('cls' if os.name == 'nt' else 'clear')

def animations(str,anim,loading_running):
    if anim == 1:
        while True:
            sys.stdout.write('\r' + str + " .")
            sleep(0.5)
            sys.stdout.write('\r' + str + " ..")
            sleep(0.5)
            sys.stdout.write('\r' + str + " ...")
            sleep(0.5)
            sys.stdout.write('\r' + str + "    ")
    elif anim == 2:
        while True:
                sys.stdout.write('\r' + str + " |")
                sleep(0.1)
                sys.stdout.write('\r' + str + " /")
                sleep(0.1)
                sys.stdout.write('\r' + str + " -")
                sleep(0.1)
                sys.stdout.write('\r' + str + " \\")
                sleep(0.1)
    elif anim == 3:
        while True:
                sys.stdout.write('\r' + str + " ■")
                sleep(0.1)
                sys.stdout.write('\r' + str + " ◆")
                sleep(0.1)

class loading:
    default_animation = 1
    "The default animation that will be used if you don't input any animation to the loading functions"

    default_string = "Loading..."
    "The string that will be used if you don't input any to the loading functions"

    loading_ended = True
    "Another easy way to keep track of any loading currently running"

    loading_running = False
    "An easy way to keep track of any loading currently running"

    def start(anim=default_animation,str=default_string):
        """A simple way of printing a loading animation\n
        Always use it inside of if __name__ == "__main__" when calling it, or else the multiprocessing will not work (On Windows)!\n
        here's an explanation of why: https://imgur.com/a/7wGch5y """
        global loading_process
        global loading_running
        global loading_ended
        loading_running = True
        loading_ended = False
        loading_process = multiprocessing.Process(target=animations,args=(str,anim,loading_running,))
        loading_process.start()


    def stop(clean=False):
        """Stops the current loading animation\n
        clean = (Clear the console after the loading is stopped)"""
        if clean == True:
            clearconsole()
        global loading_running
        global loading_ended
        loading_running = False
        loading_ended = True
        sys.stdout.write('\r                                                               \n')
        loading_process.kill()