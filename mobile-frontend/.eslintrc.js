module.exports = {
  root: true,
  extends: "expo",
  env: {
    browser: true,
    node: true,
  },
  rules: {
    "prettier/prettier": 0,
    "react-native/no-inline-styles": 0,
    "react/react-in-jsx-scope": "off",
    "react/jsx-uses-react": "off",
  },
  overrides: [
    {
      files: ["**/__tests__/**", "**/*.test.js", "jest.setup.js"],
      env: { jest: true, node: true },
    },
    {
      files: ["*.config.js", ".eslintrc.js", "babel.config.js"],
      env: { node: true },
    },
  ],
};
