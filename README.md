## Test-TCP-server

### test-tcp.py

Test script allows to create:
  * Server with specified host name and port (only for receiving messages)
  * Client for:
    * receiving a message
    * receiving a message and sending it back
    * sending a default message
    * sending a default message and waiting a response from server
    
    
Example command:

`python3 /path/to/main.py -m Message -c 50 -h localhost -p 8080 -b 16 -v 1 -s 0 -t sw`

List of options:

```
  -m [msg] if not defined - random message of -b bytes will be sent
  -c [connections] number of connections
  -h [host]
  -p [port]
  -b [b] number of bytes
  -v [verbose] -  0 - silent,
                  1 - print info,
                  2 - print all error messages
  -s [server] - 0 - only clients,
                1 - open server for listening together with clients,
                2 - only server
  -t [task] - r/receive     - receives message,
              sb/sendback   - receives nessage and sends it back,
              s/send        - sends default message
              sw/sendwait   - sends default message and waits for the response
```            

Default values:
```
port - 8080
b - 8 # bytes
connections - 1
verbose - 1
server - 1
task - sends a message
host - hostname of the machine where the program is currently executing
message - random message of 'b' bytes
```
