# !/bin/bash
ENV_NAME="rag_instagram"
REQUIREMENTS_FILE="requirements.txt"

if conda env list | grep -q "^$ENV_NAME[[:space:]]"; then
    echo "Error: Conda environment '$ENV_NAME' already exists."
    exit 1
fi

echo "Creating Conda environment '$ENV_NAME' with Python 3.11..."
conda create --name "$ENV_NAME" python=3.11 -y

# Activate the new environment
echo "Activating environment '$ENV_NAME'..."
source activate "$ENV_NAME" || conda activate "$ENV_NAME"

# Install requirements from the requirements.txt file
echo "Installing requirements from '$REQUIREMENTS_FILE'..."
pip install -r "$REQUIREMENTS_FILE"

echo "Environment '$ENV_NAME' setup complete. Activating environment..."
conda activate "$ENV_NAME"