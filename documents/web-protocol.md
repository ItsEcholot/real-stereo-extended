# Web Protocol

This document describes the protocol used for communication between the web interface and the master PI.

## WebSockets

Since many aspects of the web interface benefit from a real-time implementation, WebSockets will be used for communication.
To avoid redundancy and an overcomplex setup for the relatively small web interface, all requests will be handled over WebSockets, there will not be a separate RESTful API.

## Protocol Specification

As [socket.io](https://socket.io/) is used for implementation, their terms will be used to describe the protocol.

### Ressources

- Every resource type has its own `namespace` in the socket.io server.
- There are only top-level resources. Child resources are implemented as relations.
- If a client connects to a namespace, the current state will be sent to him.
- If a resource changes, the new state will be sent to all clients in the namespace. If the resource is related to multiple namespaces, all related namespaces will be updated.

### Events

Each resource namespace can implement the following events.
Availability of the events may depend on the actual resource type.

#### Server Events

- `get: () => Resource`<br>
Returns the current resource in the `acknowledgment`.
- `create: (data: Resource) => Acknowledgment`<br>
Creates a new resource. It should contain the whole resource in the first argument. The `acknowledgment` will contain information about the creation success and errors.
- `update: (data: Resource) => Acknowledgment`<br>
Updates the specified resource. It should contain the whole resource in the first argument and is only available on a single resource, not on a resource listing. The `acknowledgment` will contain information about the update success and errors.
- `delete: (id: number) => Acknowledgment`<br>
Deletes the specified resource. It is only available on a single resource, not on a resource listing. The `acknowledgment` will contain information about the deletion success and errors.

#### Client Events

- `get: (data: Resource | Resource[])`: This event contains the whole resource as the first argument and will be triggered each time a resource gets changed.

## Protocol Documentation

### Entities

#### `Room`

```typescript
type Room = {
  id: number;
  name: string;
  nodes: Node[];
}

type UpdateRoom = Omit<Room, 'nodes'>
type CreateRoom = Omit<UpdateRoom, 'id'>
```

#### `Node`

```typescript
type Node = {
  id: number;
  name: string;
  online: boolean;
  ip: string;
  hostname: string;
  room: Room;
}

type CreateNode = {
  name: string;
  ip: string;
  // only the `id` attribute of the room is needed
  // more can still be submitted but will be ignored
  room: {
    id: number;
  };
}
type UpdateNode = CreateNode & {
  id: number;
}
```

#### `Speaker`

```typescript
type Speaker = {
  id: number;
  name: string;
  room: Room;
}

type UpdateSpeaker = Speaker & {
  // only the `id` attribute of the room is needed
  // more can still be submitted but will be ignored
  room: {
    id: number;
  };
}
type CreateSpeaker = Omit<UpdateSpeaker, 'id'>
```

#### `Balance`

```typescript
type Balance = {
  volume: number;
  speaker: Speaker;
}
```

#### `Settings`

```typescript
type Settings = {
  configured: boolean;
  balance: boolean;
}
```

#### `Acknowledgment`

```typescript
type Acknowledgment = {
  successful: boolean;
  createdId?: number;
  errors?: string[];
}
```

### Namespaces

#### `/rooms`

Lists all saved rooms.

Available events:
- `get: () => Room[]`
- `create: (data: CreateRoom) => Acknowledgment`
- `update: (data: UpdateRoom) => Acknowledgment`
- `delete: (id: number) => Acknowledgment`

#### `/nodes`

Lists all available nodes.

Available events:
- `get: () => Node[]`
- `create: (data: CreateNode) => Acknowledgment`
- `update: (data: UpdateNode) => Acknowledgment`
- `delete: (id: number) => Acknowledgment`

#### `/speakers`

Lists all available speakers.

Available events:
- `get: () => Speaker[]`
- `create: (data: CreateSpeaker) => Acknowledgment`
- `update: (data: UpdateSpeaker) => Acknowledgment`
- `delete: (id: number) => Acknowledgment`

#### `/balances`

Lists all speakers with their current balance.

Available events:
- `get: () => Balance[]`

#### `/settings`

Shows and updates settings.

Available events:
- `get: () => Settings`
- `update: (data: Settings) => Acknowledgment`
