import { useContext, useState, useEffect } from 'react';
import { SocketContext } from './socketProvider';
import { Speaker } from './speakers';

export type Balance = {
  volume: number;
  speaker: Speaker;
}

export const useBalances = () => {
  const { getSocket, returnSocket } = useContext(SocketContext);
  const [balances, setBalances] = useState<Balance[]>();
  useEffect(() => {
    const balancesSocket = getSocket('balances');
    balancesSocket.emit('get', setBalances);
    balancesSocket.on('get', setBalances);
    return () => {
      balancesSocket.off('get', setBalances);
      returnSocket('balances');
    };
  }, [getSocket, returnSocket]);

  return { balances };
}