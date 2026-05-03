#!/bin/bash

echo "Starting Ollama server..."
ollama serve &

# Esperar a que el server levante
sleep 5

echo "Creating model..."

ollama create finetuned_mistral -f /model_files/Modelfile

echo "Running model..."
ollama run finetuned_mistral

#ollama pull llama3.2
#ollama pull nomic-embed-text