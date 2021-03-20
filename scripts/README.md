# Scripts

The following scripts are available.

## `pi-update-backend.sh`

Usage: `./pi-update-backend.sh <ip-address>`

Synchronizes the local backend code to the specified raspberry pi using rsync.
After an initial run, only changed files will get synced.

## `pi-run-backend.sh`

Usage: `./pi-run-backend.sh <ip-address> [...args]`

Runs the backend on the specified raspberry pi and shows the output.
It also synchronizes the backend code before it gets started (using `pi-update-backend.sh`) so it is always up-to-date.

Any additional arguments will directly be passed to the script.
For example, forcing a pi to run as master can be achieved like this:
`./pi-run-backend.sh 192.168.x.x --master`

## `pi-install.sh`

See [documents/raspberry-pi-setup.md](../documents/raspberry-pi-setup.md) for more information.
