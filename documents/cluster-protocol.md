# Cluster Protocol

This document describes the protocol used for communication between nodes within a cluster.

## Specifications

The port used for the protocol is `5605`.

In the direction from slave to master, messages will be sent over `UDP` while in the direction from master to slave, `TCP` is used to ensure control messages will always arrive.

The protocol is implemented using [protocol buffers](https://developers.google.com/protocol-buffers).

As protocol buffers are not self-delimiting and there is no need in the defined protocol to concatenate multiple messages in one UDP/TCP packet, there will be one message per packet.

## Messages

Since protocol buffers don't implement a way to determine which message has been sent, each message will be encapsulated in a wrapper so it can be properly decoded.

```
message Wrapper {
  uint32 app = 1;
  uint32 version = 2;
  oneof message {
    ServiceAnnouncement serviceAnnouncement = 3;
    ServiceAcquisition serviceAcquisition = 4;
    ServiceRelease serviceRelease = 5;
    PositionUpdate positionUpdate = 6;
    ServiceUpdate serviceUpdate = 7;
    Ping ping = 8;
  }
}
```

There are additional attributes on the wrapper message.

`app` is a static magic number always set to `828369` (ascii for `RSE` or `R`eal`S`tereo`E`xtended concatenated).
With this, it can be ensured that a real stereo service is running on port `5605` and not something else.

`version` contains the currently running version of real stereo.
While protocol buffers are generally forwards- and backwards-compatible, this information can be useful to display a node as `outdated` in the administration interface.

### Auto service discovery

When a node has not been acquired by a master, it will send auto service announcement messages every 15 seconds.
Those messages will be broadcasted over the whole network on port `5605`.

```
message ServiceAnnouncement {
  string hostname = 2;
}
```

`hostname` holds the hostname of the announcement sender.
The IP address can be extracted from the UDP packet header.

When a node did not recently receive a [ping](#ping) from its master, it will start sending service announcement messages again and so can be acquired by a new master.

### Service acquisition

When a master has discovered a new slave and wants to get position updates from it, he can send a service acquisition message. From then on, the slave will stop sending service discovery messages and start reporting position updates to the master.

The IP address of the master can be extracted from the TCP packet header.

```
message ServiceAcquisition {
  bool detect = 1;
}
```

`detect` indicates the current desired service status. If true, the slave will immediately start detecting people in its camera. If false, the slave will wait for a [service status update](#service-status-update) message until he starts the detection.

### Service release

When a master no longer requires the service of a slave, he can release it. The slave will then stop detection and go back into the [auto service discovery](#auto-service-discovery) mode.

```
message ServiceRelease {}
```

### Position updates

As soon as someone has been detected in the camera attached to the slave and this person has moved, a position update message will be sent to the master. This can be as frequent as every processed camera frame (multiple times per second) but at least once every 15 seconds (see [ping](#ping)).

```
message PositionUpdate {
  uint32 coordinate = 1;
}
```

### Service status update

Balancing can be started and stopped. In this case, the master will send a status update message to all slaves containing the new desired service status.

```
message ServiceUpdate {
  bool detect = 1;
}
```

### Ping

Both, master and slaves, will send ping messages to ensure the other party that they are still running and listening for updates.

For slave nodes, pings are implemented with the [position update](#position-updates) messages. As they are already sent frequently when movement is detected, they also act as ping messages so there is no need for an additional message. If no movement has been detected in the last 15 seconds, the last position update message will simply be sent again. This ensures that the master will hear from the slave at least once every 15 seconds. If that is not a case, the master will mark the node as offline.

In the other direction (master to slaves), a dedicated ping message is sent once every 60 seconds. If a slave did not receive such a message within the last minute, it will stop detection and go back into the [auto service discovery](#auto-service-discovery) mode.

```
message Ping {}
```
