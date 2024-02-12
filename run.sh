#!/bin/bash
# when start ubuntu, ollama is already running. So have to stop the current service first. 
sudo systemctl stop ollama
ollama serve 