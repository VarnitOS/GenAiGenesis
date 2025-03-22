#!/bin/bash

# Generate a secure random token
ADMIN_TOKEN=$(openssl rand -base64 32)

# Print the token
echo "Generated Admin Token: $ADMIN_TOKEN"

# Export as environment variable
export ADMIN_API_TOKEN=$ADMIN_TOKEN
echo "Exported as ADMIN_API_TOKEN environment variable"

# Save to .env file automatically
ENV_FILE="../.env"

# Check if .env file exists
if [ -f "$ENV_FILE" ]; then
    # Check if ADMIN_API_TOKEN already exists in .env
    if grep -q "ADMIN_API_TOKEN=" "$ENV_FILE"; then
        # Replace existing token
        sed -i "" "s/ADMIN_API_TOKEN=.*/ADMIN_API_TOKEN=$ADMIN_TOKEN/" "$ENV_FILE"
    else
        # Add new token
        echo "ADMIN_API_TOKEN=$ADMIN_TOKEN" >> "$ENV_FILE"
    fi
else
    # Create new .env file
    echo "ADMIN_API_TOKEN=$ADMIN_TOKEN" > "$ENV_FILE"
fi

echo "Token saved to $ENV_FILE"
echo
echo "Now testing the cleanup functionality:"
echo "Running: python scripts/test_cleanup.py --direct"
echo

# Run the test script
python scripts/test_cleanup.py --direct 