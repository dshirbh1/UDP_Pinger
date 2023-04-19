# We will need the following module to generate randomized lost packets
import random
import datetime

# Import socket module
from socket import *

# Prepare a sever socket
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(("", 12000))

while True:
    # Generate random number in the range of 0 to 10
    rand = random.randint(0, 10)

    # Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)
    # start timer
    start_time = datetime.datetime.now()

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
    serverSocket.sendto(message.encode(), address)
