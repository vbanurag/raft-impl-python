import pdb
def send_message(sock, msg):
    send_size(sock, len(msg))
    sock.sendall(msg)

def recv_messsage(sock):
    size = recv_size(sock)  # get the message size
    try:
        msg = recv_exactly(sock, size)  # Receive exactly this many bytes
    except IOError as e:
        raise IOError("Exception occurred in receive_message: " + str(e)) from e
    return msg


def send_size(sock, sz):
    sock.sendall(sz.to_bytes(8, 'big'))


def recv_size(sock):
    try:
        message = recv_exactly(sock, 8)
    except IOError as e:
        raise IOError("Exception occurred in receive_size: " + str(e)) from e
    return int.from_bytes(message, 'big')


def recv_exactly(sock, nbytes):
    '''
    Receive exactly nbytes of data on a socket
    '''
    msg = b''
    while nbytes > 0:
        chunk = sock.recv(nbytes)  # Might return partial data (whatever received so far)
        if not chunk:
            # Connection closed!
            raise IOError("Connection closed")
        msg += chunk
        nbytes -= len(chunk)
    return msg
