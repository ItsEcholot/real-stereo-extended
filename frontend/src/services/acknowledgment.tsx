export type Acknowledgment = {
  successful: boolean;
  createdId?: number;
  errors?: string[];
}