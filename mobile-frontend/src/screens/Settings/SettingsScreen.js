import React, { useContext, useMemo } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ButtonGroup, ListItem, useTheme, Icon, Button } from '@rneui/themed';
import { ThemeContext } from '../../context/ThemeContext'; // Adjust path as needed

const SettingsScreen = ({ navigation }) => {
    const { themeMode, setThemeMode, isDarkMode } = useContext(ThemeContext);
    const { theme } = useTheme();

    const themeOptions = ['Light', 'Dark', 'System'];
    const selectedIndex = useMemo(() => {
        switch (themeMode) {
            case 'light':
                return 0;
            case 'dark':
                return 1;
            case 'system':
                return 2;
            default:
                return 2;
        }
    }, [themeMode]);

    const handleThemeChange = (index) => {
        let newMode = 'system';
        if (index === 0) newMode = 'light';
        if (index === 1) newMode = 'dark';
        setThemeMode(newMode);
    };

    const styles = useMemo(
        () =>
            StyleSheet.create({
                container: {
                    flex: 1,
                    backgroundColor: theme.colors.background,
                },
                groupContainer: {
                    marginTop: 20,
                    marginHorizontal: 15,
                },
                title: {
                    fontSize: 16,
                    fontWeight: '600',
                    color: theme.colors.grey0,
                    marginBottom: 10,
                    marginLeft: 15,
                },
                buttonGroupContainer: {
                    borderRadius: 8,
                    marginHorizontal: 0, // Remove horizontal margin from ButtonGroup itself
                },
                buttonGroupSelected: {
                    backgroundColor: theme.colors.primary,
                },
                buttonGroupText: {
                    fontSize: 14,
                },
                listItem: {
                    backgroundColor: theme.colors.white,
                    paddingVertical: 15,
                },
                listItemTitle: {
                    color: theme.colors.black,
                    fontSize: 17,
                },
                listItemSubtitle: {
                    color: theme.colors.grey1,
                    fontSize: 13,
                },
                divider: {
                    // Theme handles divider color
                },
            }),
        [theme],
    );

    return (
        <ScrollView style={styles.container}>
            <View style={styles.groupContainer}>
                <Text style={styles.title}>Appearance</Text>
                <ButtonGroup
                    buttons={themeOptions}
                    selectedIndex={selectedIndex}
                    onPress={handleThemeChange}
                    containerStyle={styles.buttonGroupContainer}
                    selectedButtonStyle={styles.buttonGroupSelected}
                    textStyle={styles.buttonGroupText}
                />
            </View>

            {/* Placeholder for other settings */}
            <View style={styles.groupContainer}>
                <Text style={styles.title}>Account</Text>
                <ListItem
                    bottomDivider
                    containerStyle={styles.listItem}
                    onPress={() => alert('Navigate to Profile Edit')}
                >
                    <Icon
                        name="account-circle-outline"
                        type="material-community"
                        color={theme.colors.grey1}
                    />
                    <ListItem.Content>
                        <ListItem.Title style={styles.listItemTitle}>Edit Profile</ListItem.Title>
                    </ListItem.Content>
                    <ListItem.Chevron color={theme.colors.grey2} />
                </ListItem>
                <ListItem
                    containerStyle={styles.listItem}
                    onPress={() => alert('Navigate to Change Password')}
                >
                    <Icon
                        name="lock-outline"
                        type="material-community"
                        color={theme.colors.grey1}
                    />
                    <ListItem.Content>
                        <ListItem.Title style={styles.listItemTitle}>
                            Change Password
                        </ListItem.Title>
                    </ListItem.Content>
                    <ListItem.Chevron color={theme.colors.grey2} />
                </ListItem>
            </View>

            <View style={styles.groupContainer}>
                <Text style={styles.title}>About</Text>
                <ListItem
                    bottomDivider
                    containerStyle={styles.listItem}
                    onPress={() => alert('Show App Version')}
                >
                    <Icon
                        name="information-outline"
                        type="material-community"
                        color={theme.colors.grey1}
                    />
                    <ListItem.Content>
                        <ListItem.Title style={styles.listItemTitle}>Version</ListItem.Title>
                        <ListItem.Subtitle style={styles.listItemSubtitle}>
                            1.0.0 (Simulated)
                        </ListItem.Subtitle>
                    </ListItem.Content>
                </ListItem>
                <ListItem
                    containerStyle={styles.listItem}
                    onPress={() => alert('Show Privacy Policy')}
                >
                    <Icon
                        name="shield-lock-outline"
                        type="material-community"
                        color={theme.colors.grey1}
                    />
                    <ListItem.Content>
                        <ListItem.Title style={styles.listItemTitle}>Privacy Policy</ListItem.Title>
                    </ListItem.Content>
                    <ListItem.Chevron color={theme.colors.grey2} />
                </ListItem>
            </View>

            {/* Logout Button */}
            <View style={{ margin: 20, marginTop: 30 }}>
                <Button
                    title="Logout"
                    buttonStyle={{ backgroundColor: theme.colors.error }}
                    onPress={() => alert('Handle Logout')}
                />
            </View>
        </ScrollView>
    );
};

// Need to import ScrollView
import { ScrollView } from 'react-native';

export default SettingsScreen;
