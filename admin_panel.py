from tkinter     import Tk, messagebox
from tkinter.ttk import Notebook

from log_in_frame   import get_log_in_frame
from creating_frame import get_creating_frame
from editing_frame  import get_editing_frame
from stats_frame    import get_stats_frame

from traceback import extract_tb
def custom_excepthook(self, exc_type, exc_value, exc_traceback):

    error_text = ('Unexpected error occured. Please report error details in the: '
                  'https://github.com/Vasily3107/HTTP-Status-Code-Tester/issues\n\n'
                  'Error details:\n\n'
                 f'Type: {exc_type}\n'
                 f'Value: {exc_value}\n\n'
                  'Traceback:')

    for i, frame in enumerate(extract_tb(exc_traceback)):
        file = frame.filename.split('\\')[-1]
        error_text += f'\n{i}: {file}, line: {frame.lineno}'

    messagebox.showerror('Unexpected error', error_text)
        
    global original_report_callback_exception
    original_report_callback_exception(self, exc_type, exc_value, exc_traceback)

root = Tk()

original_report_callback_exception = Tk.report_callback_exception
root.report_callback_exception = custom_excepthook.__get__(root)

tab_switch = Notebook(root)

def after_log_in(args):
    for i in args:
        tab_switch.add(i[0](tab_switch), text=i[1])

after_log_in_args = [(get_creating_frame, 'Create tests'),
                     (get_editing_frame , 'Edit tests'  ),
                     (get_stats_frame   , 'Statistics'  )]

tab_switch.add(get_log_in_frame(tab_switch, after_log_in, after_log_in_args),
               text='Log in')
tab_switch.pack(expand=1, fill='both')

root.title('Admin Panel')
root.geometry('800x400')
root.resizable(False, False)
root.mainloop()