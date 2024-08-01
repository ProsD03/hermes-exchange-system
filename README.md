# 🪽Hermes Exchange System
The Hermes Exchange System (HXS) is an application that allows to PCs to send files between them directly, using a server as a middleman to avoid having to edit firewall rules or host a server on one of the PCs.

# Hermes Exchange Protocol
## Server Commands
### AUTH [PWD];
First command sent by server to client on connection. Confirms the connection and requires the client to authenticate. If PWD parameter is 0, no password is required: the client must simply choose a username to be identified; otherwise, the client must authenticate with an existing account.
### AUTHFAIL [REASON];
After client has sent back an AUTH packet, this is the response if the server couldn't authenticate the client. The REASON parameter is used to explain why the server couldn't authenticate. Its values can be
- 0: User not found. Not a valid reason if PWD was 0;
- 1: Wrong password. Not a valid reason if PWD was 0;
- 2: Already connected, means another user is already logged with this name/account.
### WAIT
Sent after a WRITE request by the client. Tells it to wait for the other client to accept the write request. Any data sent by the client after a WAIT packet is ignored until the other client accepts or denies the request.
### READ [CLIENT];[FILENAME];[FILESIZE];
Sent to a client which another client has asked to send data to. CLIENT parameter contains the username of the client that requested to write; FILENAME contains the name and extension of the file to be sent; FILESIZE contains the lenght of the file in bytes.
### ACCEPT
Sent to the client that requested to write to another client. Signals that the client accepted the write and server is ready to recieve data.
### DENY
Sent to the client that requested to write to another client. Signals that the client refused the write and the server won't be accepting data. Client may send another WRITE command or recieve a READ command. 


## Client Commands
### AUTH [USERNAME];[PASSWORD];
Response to auth command from server. USERNAME parameter contains the username in plaintext; PASSWORD parameter may be empty if not required by server (omit last ;) or valorized with the SHA256 hash of the password.
### WRITE [CLIENT];[FILENAME];[FILESIZE];
Request to write a file to another client. CLIENT parameter contains the username of the client to whom the client wants to write; FILENAME contains the name and extension of the file to be sent; FILESIZE contains the lenght of the file in bytes.
### ACCEPT
Sent to the server after a READ request, means that the client accepts the read and is ready to recieve data.
### DENY
Sent to the server after a READ request, means that the client refuses the write and won't be accepting data.

## Generic Commands
### OK
Generic response to other commands, like to a succesfull AUTH command from a client.
### EOF
Sent at the end of data transmission to signal the end of the data sequence.
### DATA [DATA]
Sent at the start of data transmission to signal the start of the data sequence.
