#!/usr/bin/env python2.6
import subprocess
import Tkinter as tk

# = Input demo =============================================================== #
def input_get(prompt, error_message=None, processor=None):
    if error_message is None:
        error_message = "Sorry, that didn't work. Try again"
    if processor is None:
        def require(responce):
            if not responce:
                raise Exception
            return responce
        processor = require
    
    while True:
        try:
            responce = processor(raw_input(prompt))
        except:
            print(error_message)
        else:
            return responce

def input_int(prompt):
    return input_get(prompt, error_message='Sorry, you must enter a number.',
                     processor=int)

def input_choose(prompt, selection):
    def get_selection(responce):
        index = int(responce) - 1
        if index < 0 or index >= len(selection):
            raise Exception
        return selection[index]
    return input_get(prompt, error_message="Sorry, that wasn't a valid option.",
                     processor=get_selection)

def input_demo():
    print('You entered %d' % input_int('Enter an int: '))
    print('You entered %.2f' % input_get('Enter a float: ',
        error_message='Sorry, you must enter a float', processor=float))

    selection = ('Red', 'Green', 'Blue')
    print('\n'.join('%d) %s' % (index, option)
                    for index, option in enumerate(selection, start=1)))
    print('You selected %s' % input_choose('Select colour: ', selection))


# = Media demo =============================================================== #
def media_play(path):
    subprocess.Popen('vlc -I dummy %s vlc://quit' % path, shell=True)

def media_demo():
    media_play('trailer.mp4')


# = Photograph demo ========================================================== #
def photograph_take(path):
    subprocess.check_call('streamer -o %s' % path, shell=True)

def photograph_show(path):
    subprocess.check_call('eog %s' % path, shell=True)

def photograph_demo():
    path = 'example.jpeg'
    photograph_take(path)
    photograph_show(path)


# = Simple GUI =============================================================== #
def simple_gui_demo():
    button_text = ['Click me!', 'That tickles!', 'Please stop :(',
                   'Kill the program and let the pain end']
    button_text.reverse()

    def command():
        if button_text:
            button['text'] = button_text.pop()
        else:
            root.destroy()
            exit()

    root = tk.Tk()
    root.title('Simple GUI')
    button = tk.Button(command=command, master=root, text='Click me')
    button.grid(row=0, column=0, padx=5, pady=5)
    root.mainloop()
    

# = Demo selection =========================================================== #
def main():
    named_demos = sorted((name[:-5].capitalize().replace('_', ' '), obj)
                         for name, obj in globals().iteritems()
                             if name.endswith('_demo'))
    demos = [named_demo[1] for named_demo in named_demos]

    prompt = ['Demos']
    for i, (name, _) in enumerate(named_demos, start=1):
        prompt.append('%d) %s' % (i, name))
    prompt = '\n'.join(prompt)
    print(prompt)

    input_choose('Select demo: ', demos)()
    

if __name__ == '__main__':
    main()
