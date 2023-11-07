# UDP Pinger
## Overview
Welcome to the "UDP Pinger" project! This project involves the basics of socket programming for UDP in Python. It focuses on creating a simple Ping application that can send and receive datagram packets using UDP sockets, calculate round-trip times (RTT), and compute statistics such as packet loss rate.

This README provides an overview of the project's features, implementation, and usage.

## Project Description
The "UDP Pinger" project is divided into three parts:

### Part 1: Simple UDP Pinger
In this part, you'll create a basic UDP Ping client. The client sends Ping messages to a server using UDP.
You'll implement the necessary logic for sending and receiving messages, measuring RTT, and handling potential packet loss.
### Part 2: Standard UDP Pinger
Building upon Part 1, you'll modify your Ping client to calculate and report statistics in the standard Ping program format.
You'll display the minimum RTT, maximum RTT, total number of RTTs, packet loss rate, and average RTTs.
### Part 3: Integration
In this part, you'll integrate your Standard UDP Pinger with the Project-2 implementation.
The client-side of the UDP Pinger runs on a separate thread, while the server-side of the UDP Pinger also runs on a separate thread.
How to Use
Follow these steps to set up and use the UDP Pinger:

## Prerequisites
1. Python environment with required libraries
2. Clone this repository to your local machine
3. Navigate to the project directory
4. Running the UDP Pinger
  Execute the Part 1 client (Simple UDP Pinger)
  Run the Part 2 client (Standard UDP Pinger)
5. For Part 3, you should set up the server-side and integrate it with Project-2 as specified in the project documentation.

## Testing
1. Observe the client terminal for Ping messages, RTT, and statistics.
2. Demo Screenshots
3. Please refer to the "Screenshots" directory for images of the project in action.
