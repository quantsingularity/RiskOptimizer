import { createTheme } from '@rneui/themed';

const theme = createTheme({
    lightColors: {
        primary: '#007AFF', // iOS Blue
        secondary: '#5856D6', // iOS Purple
        background: '#F2F2F7', // iOS System Gray 6
        white: '#FFFFFF',
        black: '#000000',
        grey0: '#8E8E93', // iOS System Gray
        grey1: '#AEAEB2', // iOS System Gray 2
        grey2: '#C7C7CC', // iOS System Gray 3
        grey3: '#D1D1D6', // iOS System Gray 4
        grey4: '#E5E5EA', // iOS System Gray 5
        grey5: '#F2F2F7', // iOS System Gray 6
        greyOutline: '#C7C7CC',
        searchBg: '#E5E5EA',
        success: '#34C759', // iOS System Green
        warning: '#FF9500', // iOS System Orange
        error: '#FF3B30', // iOS System Red
        disabled: '#AEAEB2',
        divider: '#C6C6C8', // iOS Separator
    },
    darkColors: {
        primary: '#0A84FF', // iOS Blue Dark
        secondary: '#5E5CE6', // iOS Purple Dark
        background: '#000000', // Black background
        white: '#FFFFFF',
        black: '#000000',
        grey0: '#EBEBF5', // Opacity 60% on Label
        grey1: '#EBEBF5', // Opacity 30% on Label
        grey2: '#EBEBF5', // Opacity 18% on Label
        grey3: '#EBEBF5', // Opacity 12% on Label
        grey4: '#3A3A3C', // iOS System Gray 4 Dark
        grey5: '#2C2C2E', // iOS System Gray 5 Dark
        greyOutline: '#48484A', // iOS System Gray 3 Dark
        searchBg: '#2C2C2E',
        success: '#30D158', // iOS System Green Dark
        warning: '#FF9F0A', // iOS System Orange Dark
        error: '#FF453A', // iOS System Red Dark
        disabled: '#48484A',
        divider: '#545458', // iOS Separator Dark
    },
    mode: 'light', // Can be 'light', 'dark', or 'auto'
    components: {
        Button: (props, theme) => ({
            buttonStyle: {
                borderRadius: 8,
                paddingVertical: 12,
            },
            titleStyle: {
                fontWeight: '600', // Semibold
                fontSize: 17,
            },
            containerStyle: {
                marginVertical: 10,
            },
            ...(props.type === 'clear' && {
                titleStyle: {
                    color: theme.colors.primary,
                    fontWeight: '400', // Regular for clear buttons
                    fontSize: 16,
                },
            }),
        }),
        Input: {
            inputContainerStyle: {
                borderBottomWidth: 0.5,
                borderColor: '#C6C6C8', // iOS Separator
                paddingHorizontal: 10,
                backgroundColor: '#FFFFFF', // White background for inputs
                borderRadius: 8,
                height: 44, // Standard iOS input height
            },
            inputStyle: {
                fontSize: 17,
            },
            placeholderTextColor: '#AEAEB2', // iOS System Gray 2
            containerStyle: {
                paddingHorizontal: 0,
                marginVertical: 8,
            },
            labelStyle: {
                fontSize: 15,
                fontWeight: '400',
                color: '#8E8E93', // iOS System Gray
                marginBottom: 4,
                marginLeft: 5,
            },
        },
        Card: {
            containerStyle: {
                borderRadius: 12,
                borderWidth: 0,
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 1 },
                shadowOpacity: 0.1,
                shadowRadius: 3,
                elevation: 2,
                margin: 15,
                padding: 15,
            },
            titleStyle: {
                fontSize: 18,
                fontWeight: '600',
                marginBottom: 10,
                textAlign: 'left',
                color: '#000000',
            },
            dividerStyle: {
                marginBottom: 10,
            },
        },
        Text: (props) => ({
            style: {
                fontSize: 17,
                color: props.h1 || props.h2 || props.h3 || props.h4 ? '#000000' : '#3C3C43', // Default text color (iOS Label)
                ...(props.style?.fontWeight === 'bold' && { fontWeight: '600' }), // Use semibold for bold
            },
            h1Style: {
                fontSize: 34,
                fontWeight: 'bold', // Will be mapped to 600
            },
            h2Style: {
                fontSize: 28,
                fontWeight: 'bold',
            },
            h3Style: {
                fontSize: 22,
                fontWeight: 'bold',
            },
            h4Style: {
                fontSize: 20,
                fontWeight: 'bold',
            },
        }),
        ListItem: {
            containerStyle: {
                paddingVertical: 12,
                paddingHorizontal: 16,
                borderBottomColor: '#C6C6C8', // iOS Separator
                borderBottomWidth: 0.5,
            },
            titleStyle: {
                fontSize: 17,
                color: '#000000',
            },
            subtitleStyle: {
                fontSize: 15,
                color: '#8E8E93', // iOS System Gray
            },
        },
        ListItemChevron: {
            color: '#AEAEB2', // iOS System Gray 2
        },
        Header: {
            backgroundColor: '#F7F7F7', // Slightly off-white background
            borderBottomColor: '#C6C6C8',
            borderBottomWidth: 0.5,
            centerComponent: {
                style: { color: '#000', fontSize: 17, fontWeight: '600' },
            },
        },
        // Add other component customizations here
    },
});

export default theme;
