rm -rf ./chroma_data/* 
rm -rf ./chroma_db/*
poetry run chroma run --host localhost --port 8000 --path ./chroma_db