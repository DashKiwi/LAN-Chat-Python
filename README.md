# LAN Chat Python

LAN Chat is a program to quickly communicate across a network in python.

## Installation

Download the files from the GitHub repository and follow the usage guide

## Usage
When running the program you will require a server and a client. Multiple clients can be created on a device meaning you can make a server and start up separate clients.

```bash
# First change your directory to the GitHub files
cd C:\Your\Path\To\Repository

# To run the server for the chats use
python server.py

# or for linux
python3 server.py

# to run the clients for the chats use
python client.py

# for linux use
python3 client.py
```
Once you have followed those steps follow the instructions on the screen.

Please note: Sometimes the program would give you an incorrect ip if you had VM's installed (or multiple internet drivers).
to fix, this on windows type "ipconfig" and find your IPv4 address and use that instead (May require trial on error)
on linux type "hostname -i" and use the first ip address there.
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
