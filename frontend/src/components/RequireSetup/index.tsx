import { FunctionComponent } from 'react';
import { Redirect, useLocation } from 'react-router';
import { useSettings } from '../../services/settings';

const RequireSetup: FunctionComponent<{}> = ({ children }) => {
  const { settings } = useSettings();
  const location = useLocation();

  // redirect to setup page if necessary
  if (settings && settings.network === 'adhoc' && !location.pathname.startsWith('/setup')) {
    return <Redirect to="/setup" />
  }

  return (
    <>
      {children}
    </>
  );
}

export default RequireSetup;
