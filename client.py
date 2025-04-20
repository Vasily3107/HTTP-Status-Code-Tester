from tkinter       import Tk, Label, messagebox, TclError
from tkinter.ttk   import Notebook, Frame

from socket        import socket, AF_INET, SOCK_STREAM, error as socket_error

disable_binary_io_loop_info_display: bool = True

if not disable_binary_io_loop_info_display:
    from colorama import init as colorama_init, Fore, Back
    colorama_init(autoreset=True)

    print(Fore.BLACK + Back.WHITE + 'Colors explained:')
    print(Back.MAGENTA + '   ' + Back.RESET + ' - binary io loops start/end')
    print(Back.GREEN   + '   ' + Back.RESET + ' - binary io loops packet iteration info')
    print()

from log_in_frame  import get_log_in_frame
from sign_up_frame import get_sign_up_frame
from tests_frame   import get_tests_frame

def after_log_in_sign_up(conn, args):
    global disable_binary_io_loop_info_display
    for i in args:
        tab_switch.add(i[0](conn, tab_switch, disable_binary_io_loop_info_display), text=i[1])

after_log_in_sign_up_args = [(get_tests_frame, 'Tests')]

def custom_excepthook(self, exc_type, exc_value, exc_traceback):

    if issubclass(exc_type, socket_error):
        messagebox.showerror('Connection error', 'Connection with the server has been lost.\n\nPlease try again later.')
        
    global original_report_callback_exception
    original_report_callback_exception(self, exc_type, exc_value, exc_traceback)

IP = "127.0.0.1"
PORT = 12345

root = Tk()

original_report_callback_exception = Tk.report_callback_exception
root.report_callback_exception = custom_excepthook.__get__(root)

tab_switch = Notebook(root)

client = socket(AF_INET, SOCK_STREAM)

connected = True

try:
    client.connect((IP, PORT))
except:
    connected = False
    connect_error_frame = Frame(tab_switch)

    Label(connect_error_frame,
          text='Sorry we couldn\'t connect you to the server\n\nPlease try again later',
          fg='red', font=20).pack(pady=(133, 0))

    tab_switch.add(connect_error_frame)

if connected:
    tab_switch.add(get_log_in_frame(client, tab_switch, after_log_in_sign_up, after_log_in_sign_up_args),
                   text='Log in')
    tab_switch.add(get_sign_up_frame(client, tab_switch, after_log_in_sign_up, after_log_in_sign_up_args),
                   text='Sign up')

def on_window_close():
    if 'frame2' in tab_switch.select():
        if not messagebox.askyesno('Closing while taking test',
                                   'Are you sure you want to exit while taking the test?\n\nYour results won\'t be saved'):
            return

    try: client.send(b'end')
    except: ...

    client.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_window_close)

tab_switch.pack(expand=1, fill='both')

root.title('Client side')
root.geometry('800x400')
root.resizable(False, False)
root.mainloop()