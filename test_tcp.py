import traceback
import logging
import time
import sys
import socket
import getopt
import datetime as dt
from dateutil.relativedelta import relativedelta
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor, as_completed
import _thread
import random
import string
import signal

'''
Command:
python3 /path/to/test_tcp.py

-m [msg] if not defined - random message of -b bytes will be sent
-c [connections] number of connections
-h [host]
-p [port]
-b [b] number of bytes
-v [verbose] -  0 - silent,
                1 - print info,
                2 - print all error messages
-s [server] - 0 - only clients,
              1 - open server for listening together with clients,
              2 - only server
-t [task] - r/receive     - receives message,
            sb/sendback   - receives nessage and sends it back,
            s/send        - sends default message
            sw/sendwait   - sends default message and waits for the response
'''


def main():

    start_time = dt.datetime.now()

    port, msg, host, b, connections, verbose, srvr, task = set_values()
    fail_conn_num = 0
    executor = ThreadPoolExecutor(max_workers=connections + 1)

    signal.signal(signal.SIGINT, interrupt)

    if srvr >= 1:
        serv = executor.submit(server, port, host, connections, b, verbose)

    if srvr != 2:
        i, elapsed, loop = 0, 0, True

        while i < connections and elapsed < 20:

            if len(msg) == 0:
                msg = rand_msg(b)
                rand = True
            else:
                rand = False

            try:
                i += 1
                if verbose > 0:
                    show_client(i, b)
                clnt = executor.submit(client, port, msg, host, b,
                                        task, verbose, i)
                if rand: msg = ''

            except:
                fail_conn_num += 1
                elapsed += 2
                if elapsed == 18:
                    print('Some error occured')
                    if verbose < 2:
                        print('Set verbose to 2 to see the traceback')
                if verbose == 2:
                    logging.error(traceback.format_exc())

    if srvr >= 1:
         for f in as_completed([serv]):
             pass
    if srvr != 2:
        for g in as_completed([clnt]):
            pass

    end_time = dt.datetime.now()

    rd = relativedelta(end_time, start_time)
    show_result(rd, fail_conn_num, connections)


def set_values():

    port, b, connections, verbose, server, task = 8080, 8, 1, 1, 1, 's'
    msg, host = b'', ''

    opts, args = getopt.getopt(sys.argv[1:], 'm:c:h:p:b:v:s:t:')

    for key, value in opts:
        if key == '-m':
            msg = value
        elif key == '-c':
            connections = int(value)
        elif key == '-h':
            host = value
        elif key == '-p':
            port = int(value)
        elif key == '-b':
            b = int(value)
        elif key == '-v':
            verbose = int(value)
        elif key == '-s':
            server = int(value)
        elif key == '-t':
            task = value

    if type(msg) != bytes:
        msg = msg.encode('utf-8')

    return port, msg, host, b, connections, verbose, server, task


def server(port, host, connections, b, verbose):

    s = ''
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if len(host) is 0:
        host = socket.gethostname()

    print('\n|Server| Starting server at port ' + str(port) +
                ' and host adress ' + host)

    server_s.bind((host, port))
    server_s.listen(connections)

    while 1:
        conn, addr = server_s.accept()
        data = conn.recv(b)

        if verbose >= 1:
            print('\n|Server| connection is established.')
            print('|Server| Address : ' + str(addr))

        print('\n|Server| received message : ' + repr(data))


def show_result(rd, fail_conn_num, connections):

    print('\nTest has finished')
    print('Test took : ' + str(rd.days) + ' days, '
                         + str(rd.hours) + ' hours, '
                         + str(rd.minutes) + ' minutes, '
                         + str(rd.seconds) + ' seconds and '
                         + str(rd.microseconds * 0.001) + ' milliseconds')

    print('Failed connections : ' +
            str(fail_conn_num) + ' out of ' + str(connections))
    print()


def show_client(i, b):

    s =  '\n================================='
    s += '\nRunning connection No : '
    s += str(i)
    s += '\n================================='

    print(s)


def rand_msg(b):
    mess = ''.join(random.choices(string.ascii_uppercase +
                                  string.ascii_lowercase +
                                  string.digits, k=b))
    return mess.encode('utf-8')


def client(port, msg, host, b, task, verbose, i):

    print('\n|No : ' + str(i) + '| Connecting to port ' +
          str(port) + ' and host adress ' + host)
    client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    r, sb, s, sw = 'r,receive,', 'sb,sendback,', 's,send,', 'sw,sendwait,'

    if len(host) is 0:
        host = socket.gethostname()

    loop, elapsed = True, 0
    while loop == True and elapsed < 20:
        try:
            client_s.connect((host, port))
            loop = False
        except ConnectionRefusedError:
            if verbose > 1:
                print('trying to recconect to the server ...')
                time.sleep(0.5)
            if elapsed > 16:
                print('Connection was refused, stopping program')
                fail_conn_num = connections
            elapsed += 2 # to prevent from the infinite loop
            pass

    if verbose > 0: print('|No : ' + str(i) +
                         '| connected, performing the task')

    if task in (s + sw)[:-1].split(','):
        if verbose >= 0: print('\n|No : ' + str(i) +
                                '| sending the message : ' + repr(msg))
        client_s.sendall(msg)
        if verbose > 0: print('|No : ' + str(i) + '| message sent')

    if task in (r + sb + sw)[:-1].split(','):
        if verbose > 0: print('|No : ' + str(i) +
                                    '| waiting for the message')
        data = client_s.recv(b)
        if verbose >= 0: print('\n|No : ' + str(i) +
                                    '| received message : ' + repr(data))

        if task in (sb)[:-1].split(','):
            time.sleep(1)
            if verbose > 0: print('|No : ' + str(i) +
                                        '| sending message back')
            client_s.sendall(data)
            if verbose > 0: print('|No : ' + str(i) + '| message sent')

def interrupt(signum, frame):
    print('Exit the program')
    sys.exit(0)

if __name__ == "__main__":
    main()
