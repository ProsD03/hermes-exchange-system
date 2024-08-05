# 🪽Hermes Exchange System
The Hermes Exchange System (HXS or simply Hermes) is an application that allows two computers to syncronously exchange files, without the need of a local server or any type of portforwarding. This keeps both computers safe, while reducing the time needed to transfer big files at a distance.
## But why? Wouldn't any cloud storage service be enough?
Not exactly. If you want to transfer a file using a cloud storage service, you'll have to wait for two steps to complete sequentially: the file upload and the file download. This means that the time necessary to transfer the file will be the sum of the time uses by both steps.
Hermes works syncronously, so while uploading the file it will be downloaded at the same time, so the total transfer time will be equal to the slower time between uploading and downloading.

Using Hermes also allows to transfer extremelly big files, because there is no intermidiary storage in the process. A cloud storage service allows to transfer files as long as they can fit in the avaiable space for your account.
## Couldn't you just use FTP to do the same thing?
Not really. FTP only allows file to be transfered between the client and the server (and vice versa), so you would still need to wait for the upload process to end before downloading the file. You would also need enough storage on the server to save the file while it is being downloaded. Hermes forwards the data packets received from the source user directly to the target user, without saving them on the server. So the transfer completes faster and no additional space is needed on the server.
