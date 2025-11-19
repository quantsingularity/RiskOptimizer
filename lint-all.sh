#!/bin/bash

# Linting and Fixing Script for RiskOptimizer Project (Python, JavaScript, HTML, CSS)

set -e  # Exit immediately if a command exits with a non-zero status

echo "----------------------------------------"
echo "Starting linting and fixing process for RiskOptimizer..."
echo "----------------------------------------"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo "Checking for required tools..."

# Check for npm/npx (for JavaScript linting)
if ! command_exists npm; then
  echo "Error: npm is required but not installed. Please install Node.js and npm."
  exit 1
else
  echo "npm is installed."
fi

if ! command_exists npx; then
  echo "Error: npx is required but not installed. Please install Node.js and npm."
  exit 1
else
  echo "npx is installed."
fi

# Check for pip/python (for Python linting)
if ! command_exists pip3; then
  echo "Error: pip3 is required but not installed. Please install Python and pip."
  exit 1
else
  echo "pip3 is installed."
fi

# Check for dos2unix - optional
if ! command_exists dos2unix; then
  echo "Warning: dos2unix is not installed. Line ending fixes will be skipped."
  DOS2UNIX_AVAILABLE=false
else
  echo "dos2unix is installed."
  DOS2UNIX_AVAILABLE=true
fi

# Install Python linting tools if needed
echo "----------------------------------------"
echo "Setting up Python linting tools..."
if ! command_exists flake8; then
  echo "Installing flake8..."
  pip3 install flake8
else
  echo "flake8 is already installed."
fi

# 1. Lint Python files
echo "----------------------------------------"
echo "Running flake8 for Python files..."
if [ -d "code/backend" ] || [ -d "code/ai_models" ]; then
  # Create a basic flake8 config if it doesn't exist
  if [ ! -f ".flake8" ]; then
    echo "Creating basic flake8 configuration..."
    cat > .flake8 << 'EOF'
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist
ignore = E203,W503
EOF
  fi

  # Run flake8 on Python files
  echo "Running flake8 on Python files..."
  python_dirs=("code/backend" "code/ai_models")
  for dir in "${python_dirs[@]}"; do
    if [ -d "$dir" ]; then
      echo "Linting Python files in $dir..."
      flake8 "$dir" || {
        echo "flake8 encountered some issues in $dir. Please review the above errors."
      }
    fi
  done
  echo "Python linting completed."
else
  echo "No Python directories found. Skipping Python linting."
fi

# 2. Lint JavaScript files in frontend
echo "----------------------------------------"
echo "Running ESLint for JavaScript files in frontend..."
if [ -d "code/frontend" ]; then
  (
    cd code/frontend
    if [ -f package.json ]; then
      echo "Found package.json. Installing npm dependencies if needed..."
      npm install --no-fund || echo "Warning: npm install failed, continuing with linting..."
    fi

    # Create a basic ESLint config if it doesn't exist
    if [ ! -f ".eslintrc.js" ] && [ ! -f ".eslintrc.json" ] && [ ! -f ".eslintrc.yml" ]; then
      echo "Creating basic ESLint configuration..."
      cat > .eslintrc.js << 'EOF'
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'warn'
  }
};
EOF
      # Install ESLint dependencies if needed
      npm install --save-dev eslint --no-fund || echo "Warning: ESLint installation failed, continuing..."
    fi

    echo "Running ESLint with --fix for JavaScript files..."
    # Use the existing lint script if available
    if grep -q "\"lint\":" package.json; then
      echo "Using existing lint script from package.json..."
      npm run lint -- --fix || {
        echo "ESLint encountered some issues in frontend. Please review the above errors."
      }
    else
      # Fallback to direct ESLint command
      npx eslint 'src/**/*.js' --fix || {
        echo "ESLint encountered some issues in frontend. Please review the above errors."
      }
    fi
    echo "ESLint completed for frontend."
  )
else
  echo "No frontend directory found. Skipping frontend ESLint."
fi

# 3. Lint JavaScript files in blockchain
echo "----------------------------------------"
echo "Running ESLint for JavaScript files in blockchain..."
if [ -d "code/blockchain" ]; then
  (
    cd code/blockchain
    if [ -f package.json ]; then
      echo "Found package.json. Installing npm dependencies if needed..."
      npm install --no-fund || echo "Warning: npm install failed, continuing with linting..."
    fi

    # Create a basic ESLint config if it doesn't exist
    if [ ! -f ".eslintrc.js" ] && [ ! -f ".eslintrc.json" ] && [ ! -f ".eslintrc.yml" ]; then
      echo "Creating basic ESLint configuration for blockchain..."
      cat > .eslintrc.js << 'EOF'
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    mocha: true
  },
  extends: [
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'warn'
  }
};
EOF
      # Install ESLint dependencies if needed
      npm install --save-dev eslint --no-fund || echo "Warning: ESLint installation failed, continuing..."
    fi

    echo "Running ESLint with --fix for JavaScript files..."
    # Use the existing lint script if available
    if grep -q "\"lint\":" package.json; then
      echo "Using existing lint script from package.json..."
      npm run lint -- --fix || {
        echo "ESLint encountered some issues in blockchain. Please review the above errors."
      }
    else
      # Fallback to direct ESLint command
      npx eslint '**/*.js' --fix || {
        echo "ESLint encountered some issues in blockchain. Please review the above errors."
      }
    fi
    echo "ESLint completed for blockchain."
  )
else
  echo "No blockchain directory found. Skipping blockchain ESLint."
fi

# 4. Lint HTML files
echo "----------------------------------------"
echo "Running HTMLHint for HTML files..."
if [ -d "code/frontend" ]; then
  (
    cd code/frontend

    # Install HTMLHint if needed
    echo "Installing HTMLHint..."
    npm install --save-dev htmlhint --no-fund || echo "Warning: HTMLHint installation failed, continuing..."

    # Create a basic HTMLHint config if it doesn't exist
    if [ ! -f ".htmlhintrc" ]; then
      echo "Creating basic HTMLHint configuration..."
      cat > .htmlhintrc << 'EOF'
{
  "tagname-lowercase": true,
  "attr-lowercase": true,
  "attr-value-double-quotes": true,
  "doctype-first": true,
  "tag-pair": true,
  "spec-char-escape": true,
  "id-unique": true,
  "src-not-empty": true,
  "attr-no-duplication": true,
  "title-require": true
}
EOF
    fi

    echo "Running HTMLHint for HTML files..."
    # Find all HTML files and run HTMLHint
    html_files=$(find . -type f -name "*.html")
    if [ -n "$html_files" ]; then
      npx htmlhint $html_files || {
        echo "HTMLHint encountered some issues. Please review the above errors."
      }
    else
      echo "No HTML files found in frontend."
    fi
    echo "HTMLHint completed."
  )
else
  echo "No frontend directory found. Skipping HTML linting."
fi

# 5. Lint CSS files
echo "----------------------------------------"
echo "Running Stylelint for CSS files..."
if [ -d "code/frontend" ]; then
  (
    cd code/frontend

    # Install Stylelint if needed
    echo "Installing Stylelint..."
    npm install --save-dev stylelint stylelint-config-standard --no-fund || echo "Warning: Stylelint installation failed, continuing..."

    # Create a basic Stylelint config if it doesn't exist
    if [ ! -f ".stylelintrc.json" ]; then
      echo "Creating basic Stylelint configuration..."
      cat > .stylelintrc.json << 'EOF'
{
  "extends": "stylelint-config-standard",
  "rules": {
    "indentation": 2,
    "string-quotes": "single",
    "no-duplicate-selectors": true,
    "color-hex-case": "lower",
    "color-hex-length": "short",
    "selector-combinator-space-after": "always",
    "selector-attribute-quotes": "always",
    "selector-attribute-operator-space-before": "never",
    "selector-attribute-operator-space-after": "never",
    "selector-attribute-brackets-space-inside": "never",
    "declaration-block-trailing-semicolon": "always",
    "declaration-colon-space-before": "never",
    "declaration-colon-space-after": "always",
    "property-no-vendor-prefix": true,
    "value-no-vendor-prefix": true,
    "number-leading-zero": "always",
    "function-url-quotes": "always",
    "font-weight-notation": "numeric",
    "font-family-name-quotes": "always-where-recommended",
    "at-rule-no-vendor-prefix": true,
    "selector-no-vendor-prefix": true,
    "media-feature-name-no-vendor-prefix": true,
    "at-rule-empty-line-before": "always"
  }
}
EOF
    fi

    echo "Running Stylelint with --fix for CSS files..."
    # Find all CSS files and run Stylelint
    css_files=$(find . -type f -name "*.css")
    if [ -n "$css_files" ]; then
      npx stylelint "$css_files" --fix || {
        echo "Stylelint encountered some issues. Please review the above errors."
      }
    else
      echo "No CSS files found in frontend."
    fi
    echo "Stylelint completed."
  )
else
  echo "No frontend directory found. Skipping CSS linting."
fi

# 6. Fix line endings (if dos2unix is available)
if [ "$DOS2UNIX_AVAILABLE" = true ]; then
  echo "----------------------------------------"
  echo "Converting line endings to Unix format..."

  # Define file extensions to process
  extensions=("py" "js" "html" "css" "json" "md" "sh")

  for ext in "${extensions[@]}"; do
    echo "Processing .$ext files..."
    find code -type f -name "*.$ext" -exec dos2unix {} \; 2>/dev/null || echo "No .$ext files found or dos2unix failed."
  done

  echo "Line ending conversion completed."
else
  echo "----------------------------------------"
  echo "Skipping line ending conversion (dos2unix not installed)."
fi

# 7. Run Prettier for consistent formatting (optional)
echo "----------------------------------------"
echo "Running Prettier for consistent code formatting..."
if [ -d "code/frontend" ]; then
  (
    cd code/frontend

    # Install Prettier if needed
    echo "Installing Prettier..."
    npm install --save-dev prettier --no-fund || echo "Warning: Prettier installation failed, continuing..."

    # Create a basic Prettier config if it doesn't exist
    if [ ! -f ".prettierrc.json" ]; then
      echo "Creating basic Prettier configuration..."
      cat > .prettierrc.json << 'EOF'
{
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "semi": true,
  "printWidth": 100
}
EOF
    fi

    echo "Running Prettier with --write for JavaScript, HTML, and CSS files..."
    npx prettier --write "**/*.{js,html,css}" || {
      echo "Prettier encountered some issues. Please review the above errors."
    }
    echo "Prettier formatting completed."
  )
else
  echo "No frontend directory found. Skipping Prettier formatting."
fi

# 8. Cleanup Unnecessary Backup and Temporary Files
cleanup_backup_files() {
  echo "----------------------------------------"
  echo "Cleaning up unnecessary backup (.bak) and temporary (.tmp) files..."

  # Define directories to clean up
  cleanup_directories=("." "code" "code/backend" "code/frontend" "code/blockchain" "code/ai_models")

  for dir in "${cleanup_directories[@]}"; do
    if [ -d "$dir" ]; then
      echo "Cleaning up in directory: $dir"
      # Find and delete all .bak and .tmp files
      find "$dir" -type f \( -name '*.bak' -o -name '*.tmp' \) -exec rm -f {} \;
      echo "Removed backup and temporary files in $dir"
    else
      echo "Directory $dir not found. Skipping cleanup for this directory."
    fi
  done

  echo "Cleanup completed."
}

cleanup_backup_files

echo "----------------------------------------"
echo "Linting and fixing process for RiskOptimizer completed!"
echo "----------------------------------------"
