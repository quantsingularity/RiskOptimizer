import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Button, Card, ListItem, Icon } from '@rneui/themed';
import { useAuth } from '../context/AuthContext';

const SettingsScreen = ({ navigation }) => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    // Add confirmation dialog before logging out
    logout();
    // Navigation back to LoginScreen is handled by AppNavigator
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Settings</Text>

      <Card containerStyle={styles.card}>
        <Card.Title>Account</Card.Title>
        <Card.Divider />
        <ListItem bottomDivider>
          <Icon name="account-circle" type="material-community" color="#555" />
          <ListItem.Content>
            <ListItem.Title>Name</ListItem.Title>
            <ListItem.Subtitle>{user?.name || 'N/A'}</ListItem.Subtitle>
          </ListItem.Content>
          {/* Add chevron and onPress to navigate to profile edit screen */}
          {/* <ListItem.Chevron /> */}
        </ListItem>
        <ListItem bottomDivider>
          <Icon name="email-outline" type="material-community" color="#555" />
          <ListItem.Content>
            <ListItem.Title>Email</ListItem.Title>
            <ListItem.Subtitle>{user?.email || 'N/A'}</ListItem.Subtitle>
          </ListItem.Content>
        </ListItem>
        {/* Add Change Password option */}
        {/* <ListItem bottomDivider onPress={() => alert('Navigate to Change Password')}>
          <Icon name="lock-reset" type="material-community" color="#555" />
          <ListItem.Content>
            <ListItem.Title>Change Password</ListItem.Title>
          </ListItem.Content>
          <ListItem.Chevron />
        </ListItem> */}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Preferences</Card.Title>
        <Card.Divider />
        <ListItem bottomDivider onPress={() => alert('Navigate to Preferences Edit')}>
           <Icon name="tune" type="material-community" color="#555" />
           <ListItem.Content>
             <ListItem.Title>Risk Tolerance</ListItem.Title>
             <ListItem.Subtitle>{user?.preferences?.risk_tolerance || 'Not Set'}</ListItem.Subtitle>
           </ListItem.Content>
           <ListItem.Chevron />
         </ListItem>
         <ListItem bottomDivider onPress={() => alert('Navigate to Preferences Edit')}>
           <Icon name="calendar-clock" type="material-community" color="#555" />
           <ListItem.Content>
             <ListItem.Title>Investment Horizon</ListItem.Title>
             <ListItem.Subtitle>{user?.preferences?.investment_horizon || 'Not Set'}</ListItem.Subtitle>
           </ListItem.Content>
           <ListItem.Chevron />
         </ListItem>
        {/* Add other preferences like notification settings */}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>About</Card.Title>
        <Card.Divider />
        <ListItem bottomDivider>
          <Icon name="information-outline" type="material-community" color="#555" />
          <ListItem.Content>
            <ListItem.Title>Version</ListItem.Title>
            <ListItem.Subtitle>1.0.0</ListItem.Subtitle> { /* Replace with dynamic version */}
          </ListItem.Content>
        </ListItem>
        {/* Add links to Privacy Policy, Terms of Service etc. */}
      </Card>

      <Button
        title="Logout"
        onPress={handleLogout}
        buttonStyle={styles.logoutButton}
        titleStyle={styles.logoutButtonTitle}
        icon={<Icon name="logout" type="material-community" color="#FF3B30" size={20} />}
        iconRight
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    margin: 20,
    color: '#333',
    textAlign: 'center',
  },
  card: {
    borderRadius: 10,
    marginBottom: 15,
    paddingBottom: 5, // Reduce bottom padding slightly
  },
  logoutButton: {
    backgroundColor: 'white',
    marginHorizontal: 15,
    marginTop: 10,
    marginBottom: 30,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FF3B30',
    paddingVertical: 12,
  },
  logoutButtonTitle: {
    color: '#FF3B30',
    fontWeight: 'bold',
    marginRight: 5,
  },
});

export default SettingsScreen;

