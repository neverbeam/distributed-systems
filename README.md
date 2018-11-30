# distributed-systems
Distributed systems Das game


ToDo:
- More parse functions
- Disconnect etc functionality in server (Martijn, fixed)
- Thread locking clients if ctrl + c -- FIX issue(Martijn, fixed)
- regex for parse functions of client input (not neccesary, skipped)
- game ticks
- correctness check of commands

Later:
- Population server
- Several server and sync
- How to deal with disconnects


issues:
- Server_input -> select in while loop is blocking, so could be that self.keep_alive change is not parsed very fast. (possible fix, game tick timeout?)

- Populator:If with no else line number 102. str(name_i) was not updated, changed it to i for time being.
