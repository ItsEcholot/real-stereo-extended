import { Room } from './rooms';

export type Node = {
  id: number;
  name: string;
  online: boolean;
  ip: string;
  hostname: string;
  room: Omit<Room, 'nodes'>;
}

export type UpdateNode = Node & {
  id: number;
  name: string;
  ip: string;
  // only the `id` attribute of the room is needed
  // more can still be submitted but will be ignored
  room: {
    id: number;
  };
}