#!/bin/bash
curl -s -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer 54088" \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen3-VL-8B-Instruct-MLX-4bit","messages":[{"role":"system","content":"回答問題"},{"role":"user","content":"什麼是RAG"}],"temperature":0.1}' | python3 -m json.tool
