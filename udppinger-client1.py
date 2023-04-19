# import socket module
from socket import *  # In order to use socket function
import time  # In order to use sleep function
import sys  # In order to terminate the program
import datetime  # In order to use datetime function

#Create a UDP socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

#Set a timeout to 1 sec
clientSocket.settimeout(1)

#IP address and port number to socket
server_ip = ""
serverPort = 12000

#Calculate number of pings should be sent
total_time = 180 #in sec
interval = 3 #in sec
total_sequence = total_time // interval
sequence_no = 1

while sequence_no <= total_sequence:
    start_time = datetime.datetime.now()
    #Arrange a msg to send
    message = "ping," + str(sequence_no) + "," + str(start_time)
    #Send the ping message to the server
    clientSocket.sendto(message.encode(), (server_ip, serverPort))
    #Is it needed?
    print(message)

    try:
        #Receive the server response
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        #If the response seq no is not the same as the seq no or time is more than 1 sec
        if modifiedMessage.decode().split(",")[1] != str(sequence_no) and (datetime.datetime.now() - start_time).seconds() >= 1:
            raise timeout
        #Calculate the RTT
        end_time = datetime.datetime.now()
        RTT = end_time - start_time
        #Is it needed?
        print(modifiedMessage.decode())
        print("RTT: " + str(RTT))

    except timeout:
        print("Client ping timed out.")

    #Sleep for 3 seconds
    time.sleep(3)


# Close the client socket
clientSocket.close()
# Terminate the program after sending the corresponding data
sys.exit()