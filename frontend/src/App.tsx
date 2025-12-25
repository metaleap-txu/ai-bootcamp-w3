import { Refine } from '@refinedev/core';
import routerBindings, {
  NavigateToResource,
  UnsavedChangesNotifier,
} from '@refinedev/react-router-v6';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';

import '@refinedev/antd/dist/reset.css';

import { dataProvider } from './providers/dataProvider';
import { ConnectionsPage } from './pages/ConnectionsPage';
import { QueryPage } from './pages/QueryPage';

function App() {
  return (
    <BrowserRouter>
      <ConfigProvider>
        <AntdApp>
          <Refine
            dataProvider={dataProvider}
            routerProvider={routerBindings}
            resources={[
              {
                name: 'connections',
                list: '/connections',
              },
              {
                name: 'queries',
                list: '/queries',
              },
            ]}
            options={{
              syncWithLocation: true,
              warnWhenUnsavedChanges: true,
            }}
          >
            <Routes>
              <Route
                index
                element={<NavigateToResource resource="queries" />}
              />
              <Route path="/connections" element={<ConnectionsPage />} />
              <Route path="/queries" element={<QueryPage />} />
              {/* TODO: Add routes for other pages */}
              {/* <Route path="/metadata" element={<MetadataPage />} /> */}
            </Routes>
            <UnsavedChangesNotifier />
          </Refine>
        </AntdApp>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default App;
