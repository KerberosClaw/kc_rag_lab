# 向量資料庫比較

## 什麼是向量資料庫？

專門儲存和搜尋高維向量的資料庫。跟傳統 SQL 資料庫不同，它用 cosine similarity 或歐氏距離來搜尋「最相似」的向量。

## 常見選擇

### ChromaDB

- 純 Python，零設定
- 存本地檔案
- 適合原型開發和學習

### Pinecone

- 全託管雲端服務
- 自動擴展
- 適合企業級應用

### pgvector

- PostgreSQL 的擴展
- 如果已有 PostgreSQL，不用多一個 DB
- SQL 查詢 + 向量搜尋混合使用

### Weaviate

- 開源，支援多模態（圖片 + 文字）
- 內建 GraphQL API

### Qdrant

- Rust 寫的，高效能
- 適合大規模部署

## Cosine Similarity

兩個向量的夾角越小，相似度越高（越接近 1）。計算公式：

```
cos(A, B) = (A · B) / (|A| × |B|)
```

大多數向量資料庫都內建了這個計算，不用自己寫。

## Embedding 維度

- 768 維：輕量，搜尋快
- 1024 維：平衡點
- 3072 維：最精準，但存儲和搜尋成本高
