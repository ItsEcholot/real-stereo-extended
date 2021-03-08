import { FunctionComponent } from 'react';
import { useRooms } from '../../services/rooms';

const OverviewPage: FunctionComponent<{}> = () => {
  const { rooms } = useRooms();

  return (
    <>
      <h1>Overview</h1>
      { JSON.stringify(rooms)}
    </>
  );
}

export default OverviewPage;