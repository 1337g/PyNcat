import socket
import sys
import time
from argparse import ArgumentParser


def parse_cl():
    parser = ArgumentParser(description='Python netcat')
    parser.add_argument('-e', '--execute', nargs=1,
                        help='Execute command on a remote host')
    parser.add_argument('-c', '--cmd', action='store_true',
                        help='Run command shell. Use "q" or "exit" to break')
    parser.add_argument('-l', '--listen', required=True,
                        help='Listen address for incoming connections')
    parser.add_argument('-p', '--port', required=True, type=int,
                        help='Listen port')
    args = parser.parse_args()
    return args


def recv_timeout(the_socket, timeout=1):
    """ Socket read method """
    the_socket.setblocking(0)
    total_data = []
    data = ''
    begin = time.time()

    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time() - begin > timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time() - begin > timeout * 2:
            break
        try:
            data = the_socket.recv(1024) # 8192
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except socket.error:
            pass

    return ''.join(total_data)[:-2]


def server(host, port):
    """ Server Method """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    conn, addr = s.accept()
    print 'Connected by', addr

    return conn


def console(conn):
    """ Run cmd shell """
    while True:
        send_data = raw_input("# ").strip()
        # check for exit
        if send_data == 'exit' or send_data == 'q':
            break
        if send_data:
            conn.sendall(send_data + '\n')
        else:
            continue
        # get response from client
        print recv_timeout(conn)

    conn.close()


def execute(conn, send_data):
    """ Execute(send) single command """
    if send_data.strip():
        conn.sendall(send_data + '\n')
        # get response from client
        print recv_timeout(conn)

    conn.close()


if __name__ == '__main__':
    args = parse_cl()

    if not args.execute and not args.cmd:
        print '[!] Not enough arguments, read help >python %s --help' % sys.argv[0]
        sys.exit()

    client = server(args.listen, args.port)

    if args.cmd:
        console(client)
    else:
        execute(client, args.execute[0])
