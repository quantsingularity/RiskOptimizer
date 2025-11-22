module.exports = {
    root: true,
    extends: '@react-native',
    parser: '@babel/eslint-parser',
    parserOptions: {
        requireConfigFile: false, // Needed if no babel.config.js
        babelOptions: {
            presets: ['@babel/preset-react'], // Assuming React preset is needed
        },
    },
    rules: {
        // Add custom rules or overrides here if needed
        'prettier/prettier': 0, // Disable prettier for now if not configured
        'react-native/no-inline-styles': 0, // Allow inline styles for simplicity
        'react/react-in-jsx-scope': 'off', // Not needed with newer React versions
        'react/jsx-uses-react': 'off', // Not needed with newer React versions
    },
};
