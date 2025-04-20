from socket import socket

from colorama import init as colorama_init, Fore, Back, Style
colorama_init(autoreset=True)

ITERATION_END_SIGNAL = b'looprecv_end_iteration'



def loopsend(connection: socket, binary_data: bytes, disable_iter_info: bool = True, packet_len: int = 1024) -> None:

    try:
        print(Back.MAGENTA + 'loopsend iteration initiated:') if not disable_iter_info else ...

        for i in range(0, len(binary_data), packet_len):

            packet = binary_data[i : i + packet_len]
            
            if not disable_iter_info:
                print(Fore.WHITE + Back.GREEN + 'loopsend packet:')
                print(f'{len(packet)=}')
                print(f'{packet=}')

            connection.sendall(packet)

        print(Back.MAGENTA + 'loopsend iteration end:') if not disable_iter_info else ...

        connection.sendall(ITERATION_END_SIGNAL)

    except ConnectionResetError:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPSEND ERROR:')
        print(Fore.RED + Style.BRIGHT + 'Connection was reset by the peer.')
    except ConnectionAbortedError:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPSEND ERROR:')
        print('Connection was aborted.')
    except TimeoutError:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPSEND ERROR:')
        print(Fore.RED + Style.BRIGHT + 'Socket operation timed out.')
    except OSError as e:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPSEND ERROR:')
        print(Fore.RED + Style.BRIGHT + f'An OS-level error occurred: {e}')
    except Exception as e:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPSEND ERROR:')
        print(Fore.RED + Style.BRIGHT + f'Unexpected error occurred: {e}')



def looprecv(connection: socket,  disable_iter_info: bool = True, packet_len: int = 1024) -> bytes:
    binary_data = b''

    try:
        print(Back.MAGENTA + 'looprecv iteration initiated:') if not disable_iter_info else ...

        while True:
            packet = connection.recv(packet_len)
            
            if not disable_iter_info:
                print(Fore.WHITE + Back.GREEN + 'looprecv packet:')
                print(f'{len(packet)=}')
                print(f'{packet=}')

            if not packet or packet == ITERATION_END_SIGNAL:
                break

            binary_data += packet

        print(Back.MAGENTA + 'looprecv iteration end:') if not disable_iter_info else ...

        return binary_data

    except ConnectionResetError:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPRECV ERROR:')
        print(Fore.RED + Style.BRIGHT + 'Connection was reset by the peer.')
    except ConnectionAbortedError:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPRECV ERROR:')
        print('Connection was aborted.')
    except TimeoutError:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPRECV ERROR:')
        print(Fore.RED + Style.BRIGHT + 'Socket operation timed out.')
    except OSError as e:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPRECV ERROR:')
        print(Fore.RED + Style.BRIGHT + f'An OS-level error occurred: {e}')
    except Exception as e:
        print(Fore.WHITE + Back.RED + 'SOCKET LOOPRECV ERROR:')
        print(Fore.RED + Style.BRIGHT + f'Unexpected error occurred: {e}')