# Build
docker build -f .\gpu-enabled.Dockerfile -t eva:gpu .

# Run with GPUs exposed and volume mount
docker run -it --gpus=all --rm -v ..:/eva eva:gpu tail -f /dev/null

# sh script/antlr4/generate_parser.sh
# pip install -e ".[dev]"

# python3 eva/eva_server.py
# python3 eva/eva_cmd_client.py