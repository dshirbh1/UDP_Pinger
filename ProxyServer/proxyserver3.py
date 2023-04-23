# Import socket module
from socket import *
from PyPDF2 import PdfReader
# In order to terminate the program
import sys
import os
# Import thread module, datetime for timestamp
import threading
import datetime
import time

#Add all variables related to ports and ip addresses
webserverUDPAddress = ""
webserverUDPPort = 12000
webserverName = ""
webserverPort = 5002
proxyserverAddress = ""
proxyserverPort = 5003
time_diff = 120.0 #in sec
time_noted = datetime.datetime.now()
started = False
total_time = 180 #in sec
ping_interval = 3 #in sec
#Path for cache
cachePath = "ProxyServer"

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
    #These variables are specifically for part 2
    min_RTT = 0
    max_RTT = 0
    total_RTT = 0
    lost_RTT = 0
    avg_RTT = 0

    #Create a UDP socket
    clientSocketUDP = socket(AF_INET, SOCK_DGRAM)
    #Set a timeout to 1 sec
    clientSocketUDP.settimeout(1)
    sequence_no = 1
    initial_start_time = datetime.datetime.now()

    while (datetime.datetime.now() - initial_start_time).seconds <= total_time:
        start_time = datetime.datetime.now()
        #Arrange a msg to send
        message = "ping," + str(sequence_no) + "," + str(start_time)
        #Send the ping message to the server
        clientSocketUDP.sendto(message.encode(), (webserverUDPAddress, webserverUDPPort))
        #Is it needed?
        print(message)

        try:
            #Receive the server response
            modifiedMessage, serverAddress = clientSocketUDP.recvfrom(2048)
            #If the response seq no is not the same as the seq no or time is more than 1 sec
            if (datetime.datetime.now() - start_time).seconds >= 1 and modifiedMessage.decode().split(",")[1] != str(sequence_no):
                raise timeout
            #Calculate the RTT
            end_time = datetime.datetime.now()
            cur_RTT = end_time - start_time
            #Is it needed?
            print(modifiedMessage.decode())
            print("RTT: " + str(cur_RTT))
            total_RTT += 1
            
            if min_RTT == 0:
                min_RTT = cur_RTT
                max_RTT = cur_RTT
                avg_RTT = cur_RTT
            else:
                min_RTT = min(min_RTT, cur_RTT)
                max_RTT = max(max_RTT, cur_RTT)
                avg_RTT += cur_RTT

        except timeout:
            print("Client ping timed out.")
            lost_RTT += 1

        #In case of keyboard interrupt, program will still calculate all the parameters
        except KeyboardInterrupt:
            break

        #Calculate the remaining time for which the code has to wait for next ping send.
        wait_time = (datetime.datetime.now() - start_time).seconds
        if wait_time < ping_interval:
            #Sleep for remaining seconds
            time.sleep(ping_interval - wait_time)

        #Increment the sequesnce_number
        sequence_no += 1
    
    #Print statements for part 2
    print("Minimum RTT : ", min_RTT)
    print("Maximum RTT : ", max_RTT)
    print("Total number of RTTs : ", total_RTT)
    print("Packet Loss rate(%) : ", (100 * lost_RTT)/(total_RTT + lost_RTT))
    print("Average RTT : ", avg_RTT/total_RTT)

    # Close the client socket
    clientSocketUDP.close()

#This is a myThread class for data and file transfer
class myThread (threading.Thread):
   def __init__(self, connectionSocket, proxyclientSocket):
      threading.Thread.__init__(self)
      self.socket = connectionSocket
      self.proxysocket = proxyclientSocket

   def run(self):
      # Get lock to synchronize threads
      threadLock.acquire()
      sendFile(self.socket, self.proxysocket)
      # Free lock to release next thread
      threadLock.release()

threadLock = threading.Lock()
threads = list()

# thread function
def sendFile(connectionSocket, proxyclientSocket):
    global started
    global time_noted
    global time_diff
    message = connectionSocket.recv(2048).decode()
    filename = message.split()[1]

    if started == True and (datetime.datetime.now() - time_noted).total_seconds() >= time_diff:
        if os.path.exists(os.path.join(cachePath, filename[1:])):
            os.remove(os.path.join(cachePath, filename[1:]))
            started = False

    if os.path.exists(os.path.join(cachePath, filename[1:])):
        if filename[1:].endswith(".html"):
            with open(os.path.join(cachePath, filename[1:]), 'r') as f:
                modifiedSentence = f.read()
            connectionSocket.send(("HTTP/1.1 200 OK\r\n\r\n" + modifiedSentence + "\r\n").encode())
            print("proxy-cache, Client, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))

        elif filename[1:].endswith("pdf"):
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
            print("proxy-cache, Client, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))
            
    else:
        #Start connecting top webserver
        proxyclientSocket = socket(AF_INET, SOCK_STREAM)
        proxyclientSocket.connect((webserverName,webserverPort))
            
        #Send the filename to Web Server
        sentence = "GET " + filename + " HTTP/1.1"
        proxyclientSocket.send(sentence.encode())
        print("proxy-forward, Server, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))
        time.sleep(0.03)

        #Receive from Web Server and close the connection with web server
        modifiedSentence = proxyclientSocket.recv(2048).decode()
        proxyclientSocket.close()

        if not os.path.exists(os.path.join(cachePath, filename[1:])):
            if "404 Not Found" not in modifiedSentence:
                with open(os.path.join(cachePath, filename[1:]), 'w') as f:
                    f.write(modifiedSentence[15:])
                    time_noted = datetime.datetime.now()
                    started = True

        connectionSocket.send(modifiedSentence.encode())
        print("proxy-forward, Client, " + str(threading.get_ident()) + ", " +  str(datetime.datetime.now()))

    # Close client socket
    connectionSocket.close()

if __name__ == '__main__':
    # Start the thread of pinging
    tPing = myThreadPing()
    tPing.start()
    threadPing.append(tPing)

    # Prepare a sever socket
    proxyserverSocket = socket(AF_INET, SOCK_STREAM)
    proxyserverSocket.bind((proxyserverAddress,proxyserverPort))
    proxyserverSocket.listen(1)

    #Handling catche files from previous run
    for item in os.listdir(cachePath):
        if not item.endswith(".py"):
            os.remove(os.path.join(cachePath, item))

    while True:
        try:
            connectionSocket, addr = proxyserverSocket.accept()
            thread = myThread(connectionSocket, proxyserverSocket)
            thread.start() #internal function of threading library
            threads.append(thread)
        except KeyboardInterrupt:
            #Shutting down the threads before ending
            for t in threads:
                t.join()
            for t in threadPing:
                t.join()
            break

    # Close server socket
    proxyserverSocket.close()
    # Terminate the program after sending the corresponding data
    sys.exit()