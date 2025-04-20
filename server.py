from socket          import socket, AF_INET, SOCK_STREAM, AddressInfo
from threading       import Thread

from colorama import init as colorama_init, Fore, Back, Style
colorama_init(autoreset=True)

from traceback import extract_tb

print(Fore.BLACK + Back.WHITE + 'Colors explained:')
print(Back.WHITE   + '   ' + Back.RESET + ' - server info')
print(Back.YELLOW  + '   ' + Back.RESET + ' - client connect/close notifications')
print(Back.RED     + '   ' + Back.RESET + ' - client logic error notifications')
print(Back.MAGENTA + '   ' + Back.RESET + ' - binary io loops start/end')
print(Back.GREEN   + '   ' + Back.RESET + ' - binary io loops packet iteration info')
print()

from jsonpickle      import (encode as jsonpickle_encode,
                             decode as jsonpickle_decode)
from binary_io_loops import loopsend, looprecv

from db_handler      import DBHandler

from client_server_shared_classes import Test, Question, Answer, Result

IP = "127.0.0.1"
PORT = 12345
CLIENTS_LIMIT = 10

server = socket(AF_INET, SOCK_STREAM)
server.bind((IP, PORT))
server.listen(CLIENTS_LIMIT)

clients: list[Thread] = []
waiting = 0

def show_server_info() -> None:
    global clients, waiting

    from time import sleep

    while True:
        print(Fore.BLACK + Back.WHITE + 'server thread info:')
        print(f'    active: {len(clients)}')
        print(f'   waiting: {waiting}\n')
        sleep(10)
Thread(target=show_server_info, daemon=True).start()

def client_logic(thread_index:int, conn:socket, addr:AddressInfo) -> None:
    client_uuid = None
    try:
     while True:
      match conn.recv(1024).decode():
       case 'log_in':
           data = jsonpickle_decode(conn.recv(1024))
       
           login    = data['login']
           password = data['password']
       
           res = DBHandler.log_in(login, password)
       
           if res: client_uuid = res
       
           conn.send(jsonpickle_encode(
               {'response' : bool(res)}
           ).encode())
       
       case 'sign_up':
           data = jsonpickle_decode(conn.recv(1024))
       
           login    = data['login']
           password = data['password']
       
           res = DBHandler.sign_up(login, password)
       
           if res: client_uuid = res
       
           conn.send(jsonpickle_encode(
               {'response' : bool(res)}
           ).encode())
       
       case 'get_tests':
           res = DBHandler.get_tests(client_uuid)
       
           binary_data = jsonpickle_encode(
                            {'response' : res}
                         ).encode()

           loopsend(conn, binary_data, False)

       case 'get_q_and_a':
           test_name = conn.recv(1024).decode()
           
           q_list, a_list = DBHandler.get_questions_answers(test_name)

           hide_is_correct_a_list: list[Answer] = [] + a_list
           for a in hide_is_correct_a_list: a.is_correct
           
           binary_data = jsonpickle_encode(
                             {'response' : [q_list, hide_is_correct_a_list]}
                         ).encode()

           loopsend(conn, binary_data, False)

           binary_data = looprecv(conn, False)

           if binary_data == b'end'        : break
           if binary_data == b'test_cancel': continue

           user_answers: list[Answer] = jsonpickle_decode(binary_data)['user_answers']

           correct_answers = 0
           answer_results = [] # [(q_text, a_text, a_is_correct)]

           for a in user_answers:
               a.is_correct, a.text = next((i.is_correct, i.text) for i in a_list if i.uuid == a.uuid)

               answer_results.append([next(q.text for q in q_list if q.uuid == a.question_uuid), a.text, a.is_correct])

               correct_answers += a.is_correct

           loopsend(conn, jsonpickle_encode({'results': (answer_results, str(int(correct_answers/len(q_list)*100))+'%')}).encode(), False)

           DBHandler.save_user_results(client_uuid, q_list[0].test_uuid, correct_answers/len(q_list), user_answers)

       case 'end': break

    except ConnectionResetError:
        ...
    except Exception as e:
        print(Back.RED + f'Client error: IP address = {addr[0]}:{addr[1]} | UUID = {client_uuid}')
        print(Fore.RED + Style.BRIGHT + 'Details: ' + e.__str__())
        print(Fore.RED + Style.BRIGHT + 'Traceback:')
        tb = extract_tb(e.__traceback__)
        for i, frame in enumerate(tb):
            file = frame.filename.split('\\')[-1]
            print(Fore.RED + Style.BRIGHT + f'{i}: file: {file}, line: {frame.lineno}, path: {frame.filename}')

    print(Back.YELLOW + Style.BRIGHT + f'Client connection closed: IP address = {addr[0]}:{addr[1]} | UUID = {client_uuid}')
    conn.close()
    thread_end(thread_index)

def thread_end(thread_index:int) -> None:
    global clients, waiting

    clients.pop(thread_index)

    if not waiting:
        thread_start()

def thread_start() -> None:
    global clients, waiting

    waiting += 1
    conn, addr = server.accept()
    print(Back.YELLOW + Style.BRIGHT + f'Client connection initiated: IP address = {addr[0]}:{addr[1]}')
    waiting -= 1

    new_thread = Thread(target=client_logic,
                        args=(len(clients), conn, addr),
                        daemon=True)
    new_thread.start()

    clients.append(new_thread)

    if len(clients) < CLIENTS_LIMIT:
        thread_start()

thread_start()