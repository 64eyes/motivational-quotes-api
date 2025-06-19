from flask import Flask, request, jsonify
import numpy as np
import faiss
import threading

app = Flask(__name__)

# In-memory FAISS index (L2 distance, 1536 dims for OpenAI embeddings)
DIM = 1536
index = faiss.IndexFlatL2(DIM)
quote_ids = []  # List to map index positions to quote_ids
lock = threading.Lock()

@app.route('/add_embedding', methods=['POST'])
def add_embedding():
    data = request.json
    embedding = np.array(data['embedding'], dtype='float32').reshape(1, -1)
    quote_id = data['quote_id']
    with lock:
        index.add(embedding)
        quote_ids.append(quote_id)
    return jsonify({'status': 'success'})

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    embedding = np.array(data['embedding'], dtype='float32').reshape(1, -1)
    top_k = int(data.get('top_k', 5))
    with lock:
        if index.ntotal == 0:
            return jsonify({'results': []})
        D, I = index.search(embedding, top_k)
        results = [quote_ids[i] for i in I[0] if i < len(quote_ids)]
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 