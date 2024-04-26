# Seppuku

TCP Driven violent Linux reboot

## Description

I've lost some remote raspberry-pi based setups due to bad USB connection between a SSD and the USB bus.
This thing listens for TCP connection on port `58192` (by default), when sent the right string, it reboots violently the host through a sysrq request.

Because it already resides in memory, is running and listening, there is a good chance that in case of a lost connectivity with storage the host will recover after a hard reboot.   

It is bad, but avoids me a trip to physically reboot the damn thing.


## Environment variables

 - `SEPPUKU_LISTEN` (default `0.0.0.0`) contains the listening address for the socket
 - `SEPPUKU_PORT` (default `55192`) is the TCP port on which the script will listen
 - `SEPPUKU_PASSWORD` (default empty) contains the password to reboot the machine, if empty, a random 24 character one will be generated

## Usage once running

```shell
# netcat will do the trick
echo "ping" | nc my.remote.host 55192
> pong#
echo "reboot:xGtKdKlPsDns" | nc my.remote.host 55192

```

## Security

Absolutely none. Put at least setup some firewall rules to secure this thing a tiny bit. Also everything sent to it is logged to stdout/stderr