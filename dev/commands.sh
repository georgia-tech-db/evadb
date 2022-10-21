# Build from the parent directory
docker build -f .\dev\gpu-enabled.Dockerfile -t eva:gpu .

# Run with GPUs exposed and volume mount
docker run -it --gpus=all --rm -v  D:\Projects\eva:/eva eva:gpu tail -f /dev/null

# python3 eva/eva_server.py
# python3 eva/eva_cmd_client.py