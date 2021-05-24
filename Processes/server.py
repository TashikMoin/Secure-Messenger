import socket
import sys
import os
import threading

isTerminated = False

def API(first_peer, second_peer, current_peer_context):
    global isTerminated
    recv_message = " "
    while recv_message != 'q':
        if isTerminated == True:
            break
        if current_peer_context == 'first':
            recv_message = str(first_peer.recv(1024).decode('utf-8')) 
            # recv from client # 1
            second_peer.send(bytes(recv_message, "utf-8"))            
            # send received message to client # 2
        elif current_peer_context == 'second':
            recv_message = str(second_peer.recv(1024).decode('utf-8')) 
            # recv from client # 2
            first_peer.send(bytes(recv_message, "utf-8"))              
            # send received message to client # 1
    isTerminated = True
    first_peer.close()
    second_peer.close()


clients_list = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', int(sys.argv[1]) ))
server_socket.listen(10)
print("Server started listening on port # " + str(sys.argv[1]) )
print("Note: Enter 'q' to terminate connections")
while True:
    first_peer, client_information = server_socket.accept()
    clients_list.append(client_information)
    if os.fork() == 0 :
        server_socket.close() 
        print(f"\nServer got a new connection with ip {client_information[0]} and port {client_information[1]}")

        while True:
            mode = str(first_peer.recv(1024).decode("utf-8"))
            if mode == 'connect':
                first_peer.send(bytes(str(clients_list), "utf-8"))
                second_peer_ip = '' 
                second_peer_port = ''
                second_peer_ip = str(first_peer.recv(1024).decode("utf-8"))
                second_peer_port = str(first_peer.recv(1024).decode("utf-8"))
                second_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    second_peer.connect((second_peer_ip, int(second_peer_port) ))
                    first_peer_thread = threading.Thread(target=API, args=(first_peer, second_peer, 'first'))
                    first_peer_thread.start()
                    second_peer_thread = threading.Thread(target=API, args=(first_peer, second_peer, 'second'))
                    second_peer_thread.start()
                except socket.error as msg:
                    print(f'Socket Error: {msg}')

            if mode == 'wait':
                first_peer.send(bytes(str(client_information[0]), "utf-8"))
