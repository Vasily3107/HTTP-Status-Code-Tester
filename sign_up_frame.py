from tkinter         import Label, Button, Entry
from tkinter.ttk     import Notebook, Frame

from socket          import socket
from jsonpickle      import (encode as jsonpickle_encode,
                             decode as jsonpickle_decode)

from typing import Callable

def get_sign_up_frame(conn: socket,
                      tab_switch: Notebook,
                      after_sign_up: Callable,
                      after_sign_up_args: list[tuple[Callable, str]]) -> Frame:
    sign_up_frame = Frame(tab_switch, name='sign_up_frame')

    login_subframe = Frame(sign_up_frame, padding=10)
    Label(login_subframe, text='Login:', width=10).grid(row=0, column=0)
    login_entry = Entry(login_subframe)
    login_entry.grid(row=0, column=1)
    login_subframe.pack(pady=(50, 0))

    password_subframe = Frame(sign_up_frame, padding=10)
    Label(password_subframe, text='Password:', width=10).grid(row=0, column=0)
    password_entry = Entry(password_subframe, show='*')
    password_entry.grid(row=0, column=1)
    password_subframe.pack()

    conf_pas_subframe = Frame(sign_up_frame, padding=10)
    Label(conf_pas_subframe, text='Confirm\npassword:', width=10).grid(row=0, column=0)
    conf_pas_entry = Entry(conf_pas_subframe, show='*')
    conf_pas_entry.grid(row=0, column=1)
    conf_pas_subframe.pack()

    def send_sign_up_info() -> None:
        info_label.config(text='', fg='black')

        login    = login_entry.get()
        password = password_entry.get()
        conf_pas = conf_pas_entry.get()

        if not len(login)      : info_label.config(text='Error: login cannot be empty'   , fg='red'); return
        if not len(password)   : info_label.config(text='Error: password cannot be empty', fg='red'); return
        if password != conf_pas: info_label.config(text='Error: passwords do NOT match'  , fg='red'); return

        conn.send(b'sign_up')
        conn.send(jsonpickle_encode(
            {'login'   : login,
             'password': password}
        ).encode())
        res = jsonpickle_decode(conn.recv(1024))['response']

        if res:
            if '.test_frame' not in ' '.join(tab_switch.tabs()):
                after_sign_up(conn, after_sign_up_args)

            info_label.config(text=f'Signed up as: {login}', fg='green')
            return

        info_label.config(text=f'Error: name {login} is taken', fg='red')

    Button(sign_up_frame, text='Log in', command=send_sign_up_info, width=30).pack()

    info_label = Label(sign_up_frame, height=2)
    info_label.pack()

    return sign_up_frame