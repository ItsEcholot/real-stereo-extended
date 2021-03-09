import { Room } from './rooms';

export type Node = {
  id: number;
  name: string;
  online: boolean;
  ip: string;
  hostname: string;
  room: Room;
}

export type UpdateNode = Node & {
  // only the `id` attribute of the room is needed
  // more can still be submitted but will be ignored
  room: {
    id: number;
  };
}
export type CreateNode = Omit<UpdateNode, 'id'>