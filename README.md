# Check Point Requests (CPR)

Command line tool for Check Point API requests on any operating system.

Built with ``python3``.

Run with ``./cpr.sh`` on Linux/Mac. ``python3 cpr.py`` on Windows.

#### Check Point API workflow

1. ``login`` to create an active session
2. Do work (add/show/change/remove objects)
3. ``publish`` or ``discard`` your work
4. ``logout`` to terminate your session

#### Lists

If you have to build a request with lists of objects such as adding multiple hosts to a new group:

```shell
POST {{server}}/add-group
Content-Type: application/json
X-chkp-sid: {{session}}

{
  "name" : "New Group 4",
  "members" : [ "New Host 1", "My Test Host 3" ]
}
```

The script will expect the members objects to be contained in quotes(``"``) with commas as delimiters(``,``). 

For example: ``python3 cpr.py add-group name "New Group 4" members "New Host 1, My Test Host 3"``

Make sure you build the host objects before running this command.

#### Key Value Pairs

If you have to build a request with an embedded key-value pair like adding new hosts to an existing group:

```shell
POST {{server}}/set-group
Content-Type: application/json
Ses: 
X-chkp-sid: {{session}}

{
  "name" : "New Group 1",
  "members" : {
    "add" : "New Host 1", "My Test Host 3"
  },
}
```

The script will expect a colon(``:``) to denote the nested key-value pairs.

For example: ``python3 cpr.py set-group name "New Group 1" members "add:My Test Host 3,New Host 1"``