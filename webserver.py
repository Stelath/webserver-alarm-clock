import socket
import threading
import platform
import os
import gpiozero
from gpiozero import DigitalInputDevice


def play_sound(sound):
    if platform.system() == 'Linux':
        os.system("aplay " + sound)
    elif platform.system() == 'Darwin':
        os.system("afplay " + sound)
    else:
        print('Platform not supported')


def stop_sound():
    if platform.system() == 'Linux':
        os.system("killall aplay")
    elif platform.system() == 'Darwin':
        os.system("killall afplay")
    else:
        print('Platform not supported')


def wakeup(query):
    if query == None:
        return get_index('Didn\'t Enter Password')

    if query[0] == ('pswd=' + PASSWORD):
        play_sound_thread = threading.Thread(target=play_sound, args=('alarm.wav',), daemon=True)
        play_sound_thread.start()

        return get_file('/html/wakeup.html')
    else:
        return get_index('Incorrect Password')


def get_index(error):
    fin = open('htdocs/index.html')
    content = fin.read()
    fin.close()

    if error != '':
        split_content: list[str] = content.split('<!-- Placeholder for Error -->')
        content = split_content[0] + '<p class=\'error\'>' + error + '</p>' + split_content[1]

    response = 'HTTP/1.0 200 OK\n\n' + content

    return response


def get_file(filename):
    try:
        fin = open('htdocs' + filename)
        content = fin.read()
        fin.close()

        response = 'HTTP/1.0 200 OK\n\n' + content
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'

    return response


def handle_request(request):
    headers = request.split('\n')
    filename = headers[0].split()[1].split('?', 1)[0]

    try:
        query = headers[len(headers) - 1].split('&')
    except IndexError:
        query = None

    urlMap = {
        '/': get_index(''),
        '/index.html': get_index(''),
        '/wakeup.html': wakeup(query)
    }

    try:
        response = urlMap[filename]
    except KeyError:
        response = get_file(filename)

    return response


# Define GPIO input
# push_button: DigitalInputDevice = gpiozero.DigitalInputDevice(27)
# push_button.when_activated = stop_sound

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 80

# Define a password to wakeup
PASSWORD = ''

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

while True:
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()
    print(request)

    # Return an HTTP response
    response = handle_request(request)
    client_connection.sendall(response.encode())

    # Close connection
    client_connection.close()

# Close socket
server_socket.close()
