// App.js
import React from 'react';
import { Container, Paper, Title } from '@mantine/core';
import MapComponent from './MapComponent';

function App() {
  return (
    <Container>
      <Title align="center" my="lg">My Map Application</Title>
      <Paper shadow="sm" padding="md" radius="lg" style={{ height: '600px', width: '600px', margin: 'auto' }}>
        <MapComponent />
      </Paper>
    </Container>
  );
}

export default App;