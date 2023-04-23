# Import socket module
from socket import *
from PyPDF2 import PdfReader
# In order to terminate the program
import sys
# Import thread module
import threading
import datetime
import random

#This is a myThreadPing class for pinging
class myThreadPing (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Get lock to synchronize threads
        threadLockPing.acquire()
        pingAction()
        # Free lock to release next thread
        threadLockPing.release()

threadLockPing = threading.Lock()
threadPing = list()

# thread function
def pingAction():
    # Notice the use of SOCK_DGRAM for UDP packets
    serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
    wait_time = 30 #in sec
    serverSocketUDP.settimeout(wait_time)
    # Assign IP address and port number to socket
    serverSocketUDP.bind(("", 12000))
    
    while True:
        try:
            # Generate random number in the range of 0 to 10
            rand = random.randint(0, 10)

            # Receive the client packet along with the address it is coming from
            message, address = serverSocketUDP.recvfrom(2048)
            # start timer
            initial_time = datetime.datetime.now()

            # If rand is less is than 4, we consider the packet lost and do not respond
            if rand < 4:
                continue

            # Otherwise, prepare the server response
            # message is one line consisting of ASCII characters in the following format:
            # echo,SEQUENCE-NUMBER,TIMESTAMP
            # Where "SEQUENCE-NUMBER" is the same as the sequence number in the client ping
            # message, and "TIMESTAMP" is the time when the server sends the messag

            message = message.decode()
            # split the message into a list
            message = message.split(",")
            # change the first element to echo
            message[0] = "echo"

            # update timestamp
            message[2] = str(datetime.datetime.now())
            # join the list back into a string
            message = ",".join(message)

            # The server responds
            serverSocketUDP.sendto(message.encode(), address)

        except TimeoutError or socket.timeout or BaseException:
            print("Server echo timed out.")
            break

    #closing the socket and thread as well
    serverSocketUDP.close()


#This is a myThread class for data and file transfer
class myThread (threading.Thread):
    def __init__(self, connectionSocket):
        threading.Thread.__init__(self)
        self.socket = connectionSocket

    def run(self):
        # Get lock to synchronize threads
        threadLock.acquire()
        sendFile(self.socket)
        # Free lock to release next thread
        threadLock.release()

threadLock = threading.Lock()
threads = list()

# thread function
def sendFile(connectionSocket):
    try:
        message = connectionSocket.recv(2048).decode()
        filename = message.split()[1]
            
        if filename.endswith("pdf"):
            reader = PdfReader(filename[1:], 'rb')
            number_of_pages = len(reader.pages) ##len(reader.pages)
                
            current_page = 0
            whole_text = ""
            while current_page < number_of_pages:
                # getting a specific page from the pdf file
                page = reader.pages[current_page]
                
                # extracting text from page
                outputdata = page.extract_text()
                whole_text = whole_text + outputdata
                current_page += 1
            # Send one HTTP header line into socket with data
            connectionSocket.send(("HTTP/1.1 200 OK\r\n\r\n" + whole_text + "\r\n").encode())
            print("server-response, 200 OK, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))
            
        elif filename.endswith("html"):
            f = open(filename[1:])
            outputdata = f.read()

            # Send one HTTP header line into socket
            connectionSocket.send(("HTTP/1.1 200 OK\r\n\r\n" + outputdata + "\r\n").encode())
            print("server-response, 200 OK, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))

    except IOError:
        # Send response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n File not found \r\n".encode())
        print("server-response, 404 Not Found, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))

    # Close client socket
    connectionSocket.close()

if __name__ == '__main__':
    # Start the thread of pinging
    tPing = myThreadPing()
    tPing.start()
    threadPing.append(tPing)

    # Prepare a sever socket
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverPort = 5002
    serverAddress = ""
    serverSocket.bind((serverAddress,serverPort))
    serverSocket.listen(1)
    while True:
        try:
            # Establish the connection
            connectionSocket, addr = serverSocket.accept()
            thread = myThread(connectionSocket)
            thread.start()
            threads.append(thread)
        except KeyboardInterrupt:
            #Shutting down the threads before ending
            for t in threads:
                t.join()
            for t in threadPing:
                t.join()
            break

    # Close server socket
    serverSocket.close()
    # Terminate the program after sending the corresponding data
    sys.exit()