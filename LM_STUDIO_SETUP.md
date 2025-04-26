# Setting up CodeBridge AI with LM Studio's GLM-4-0414

This guide will help you set up and run CodeBridge AI with your LM Studio GLM-4-0414 model.

## Step 1: Configure LM Studio

1. Open LM Studio on your Mac
2. Load your GLM-4-0414 model if it's not already loaded
3. Go to Settings
4. Enable the "Local Server" option (if not already enabled)
5. Make sure the port is set (default is usually 1234)
6. Click "Start server" if it's not already running

## Step 2: Install or Update Dependencies

```bash
# In your project directory
cd /Users/vithushanjeyapahan/Documents/GitHub/codebridge-ai
pip install -r requirements.txt
```

## Step 3: Running CodeBridge AI with LM Studio

```bash
# If you haven't processed your documents yet, run:
cd /Users/vithushanjeyapahan/Documents/GitHub/codebridge-ai
python src/main.py --setup

# To use with LM Studio's GLM-4-0414:
python src/main.py
```

By default, the application will use LM Studio with GLM-4-0414 as the model.

## Command Line Options

You can customize the run with these options:

```bash
# Specify a different model
python src/main.py --model "Your-Model-Name"

# Use a different port for LM Studio (if not using the default 1234)
python src/main.py --lmstudio-url http://localhost:8080

# Switch to Ollama (if you have it installed)
python src/main.py --provider ollama --model codellama:7b
```

## Troubleshooting

If you encounter any issues:

1. **LM Studio API not accessible**: 
   - Make sure LM Studio is running
   - Verify the "Local Server" option is enabled in LM Studio settings
   - Check that a model is loaded and active
   - Confirm the server is started

2. **Incorrect port**: 
   - Check which port LM Studio is using in its settings
   - Use the `--lmstudio-url` parameter with the correct port

3. **No documents found**: 
   - Run the setup command to process your documentation:
   ```bash
   python src/main.py --setup
   ```

4. **Model not responding**: 
   - Make sure you've selected and started a model in LM Studio
   - Try restarting LM Studio if the model is loaded but not responding
