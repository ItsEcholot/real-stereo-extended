# Web Protocol

This document describes the protocol used for communication between the web interface and the master PI.

## WebSockets

Since many aspects of the web interface benefit from a real-time implementation, WebSockets will be used for communication.
To avoid redundancy and an overcomplex setup for the relatively small web interface, all requests will be handled over WebSockets, there will not be a separate RESTful API.

## Protocol Specification

As [socket.io](https://socket.io/) is used for implementation, their terms will be used to describe the protocols.

### Ressources

- Every resource type has its own `room`.
- A resource may be a child resource of another one. In this case, they are concatenated by a forward slash `/`.
- There can be `rooms` for resource listings (e.g. `cameras`) and single resources (e.g. `cameras/1`).
- If a client connects to a `room`, the current state will be sent to him.
- If a resource changes, the new state will be sent to all clients in the `room`. If the resource is related to multiple `rooms`, all related `rooms` will be updated.

### Events

Each resource `room` can implement the following events.
Availability of the events may depend on the actual resource type.

#### Server Events

- `create: (data: Resource) => Acknowledgment`<br>
Creates a new resource. It should contain the whole resource in the first argument. It is only available on a resource listing, not on a single resource. The `acknowledgment` will contain information about the creation success and errors.
- `update: (data: Resource) => Acknowledgment`<br>
Updates the specified resource. It should contain the whole resource in the first argument and is only available on a single resource, not on a resource listing. The `acknowledgment` will contain information about the update success and errors.
- `delete: () => Acknowledgment`<br>
Deletes the specified resource. It is only available on a single resource, not on a resource listing. The `acknowledgment` will contain information about the deletion success and errors.

#### Client Events

- `get: (data: Resource | Resource[])`: This event will get fired automatically after joining a `room` and when the resource gets changed. It contains the whole resource as the first argument.

## Protocol Documentation

### Entities

#### `Room`

```typescript
// listing
type Room = {
  id: number;
  name: string;
}

// single
type SingleRoom = Room & {
  nodes: Node[];
  speakers: Speaker[];
}
```

#### `Node`

```typescript
// listing
type Node = {
  id: number;
  name: string;
  online: boolean;
}

// single
type SingleNode = Node & {
  ip: string;
  hostname: string;
  room: Room;
}
```

#### `Speaker`

```typescript
// listing
type Speaker = {
  id: number;
  name: string;
}
```

#### `Balance`

```typescript
// listing
type Balance = {
  volume: number;
  speaker: Speaker;
}
```

#### `Settings`

```typescript
// single
type Settings = {
  balance: boolean;
}
```

#### `Acknowledgment`

```typescript
// single
type Acknowledgment = {
  successful: boolean;
  errors?: string[];
}
```

### Rooms

#### `rooms`

Lists all saved rooms.

Available events:
- `get: () => Room[]`
- `create: (data: Room) => Acknowledgment`

#### `rooms/:id`

Shows or updates a selected room.

Available events:
- `get: () => SingleRoom`
- `update: (data: SingleRoom) => Acknowledgment`
- `delete: () => Acknowledgment`

#### `nodes`

Lists all available nodes.

Available events:
- `get: () => Node[]`
- `create: (data: Node) => Acknowledgment`

#### `nodes/:id`

Shows or updates a selected node.

Available events:
- `get: () => SingleNode`
- `update: (data: SingleNode) => Acknowledgment`
- `delete: () => Acknowledgment`

#### `balances`

Lists all speakers with their current balance.

Available events:
- `get: () => Balance[]`

#### `settings`

Shows and updates settings.

Available events:
- `get: () => Settings`
- `update: (data: Settings) => Acknowledgment`
