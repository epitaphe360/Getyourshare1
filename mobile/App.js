/**
 * ShareYourSales Mobile App
 * Main Application Component
 */

import React from 'react';
import {StatusBar, LogBox} from 'react-native';
import {NavigationContainer} from '@react-navigation/native';
import {GestureHandlerRootView} from 'react-native-gesture-handler';
import {Provider as PaperProvider} from 'react-native-paper';
import {AuthProvider} from './src/contexts/AuthContext';
import {ToastProvider} from './src/contexts/ToastContext';
import RootNavigator from './src/navigation/RootNavigator';
import theme from './src/utils/theme';

// Ignore specific warnings
LogBox.ignoreLogs([
  'Non-serializable values were found in the navigation state',
]);

const App = () => {
  return (
    <GestureHandlerRootView style={{flex: 1}}>
      <PaperProvider theme={theme}>
        <AuthProvider>
          <ToastProvider>
            <NavigationContainer>
              <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
              <RootNavigator />
            </NavigationContainer>
          </ToastProvider>
        </AuthProvider>
      </PaperProvider>
    </GestureHandlerRootView>
  );
};

export default App;
