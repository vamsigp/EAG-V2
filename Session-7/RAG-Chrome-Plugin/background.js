// Background service worker for RAG Web Indexer
importScripts('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.10.0/dist/tf.min.js');
importScripts('https://cdn.jsdelivr.net/npm/@tensorflow-models/universal-sentence-encoder@1.3.3/dist/universal-sentence-encoder.min.js');

class RAGIndexer {
    constructor() {
        this.model = null;
        this.faissIndex = null;
        this.urlMappings = new Map();
        this.isModelLoading = false;
        this.isModelLoaded = false;

        // Initialize on startup
        this.init();
    }

    async init() {
        console.log('RAG Indexer: Initializing...');
        await this.loadStoredData();
        await this.loadModel();
    }

    async loadModel() {
        if (this.isModelLoading || this.isModelLoaded) return;

        this.isModelLoading = true;
        try {
            console.log('RAG Indexer: Loading Universal Sentence Encoder...');
            this.model = await use.load();
            this.isModelLoaded = true;
            console.log('RAG Indexer: Model loaded successfully');
        } catch (error) {
            console.error('RAG Indexer: Failed to load model:', error);
        } finally {
            this.isModelLoading = false;
        }
    }

    async loadStoredData() {
        try {
            const result = await chrome.storage.local.get(['faissIndex', 'urlMappings']);

            if (result.faissIndex) {
                this.faissIndex = result.faissIndex;
                console.log('RAG Indexer: Loaded FAISS index with', this.faissIndex.length, 'entries');
            } else {
                this.faissIndex = [];
            }

            if (result.urlMappings) {
                this.urlMappings = new Map(result.urlMappings);
                console.log('RAG Indexer: Loaded', this.urlMappings.size, 'URL mappings');
            }
        } catch (error) {
            console.error('RAG Indexer: Failed to load stored data:', error);
            this.faissIndex = [];
        }
    }

    async saveStoredData() {
        try {
            await chrome.storage.local.set({
                faissIndex: this.faissIndex,
                urlMappings: Array.from(this.urlMappings.entries())
            });
            console.log('RAG Indexer: Data saved successfully');
        } catch (error) {
            console.error('RAG Indexer: Failed to save data:', error);
        }
    }

    async generateEmbedding(text) {
        if (!this.isModelLoaded) {
            await this.loadModel();
        }

        if (!this.model) {
            throw new Error('Model not loaded');
        }

        try {
            const embeddings = await this.model.embed([text]);
            const embeddingArray = await embeddings.data();
            embeddings.dispose(); // Clean up memory
            return Array.from(embeddingArray);
        } catch (error) {
            console.error('RAG Indexer: Failed to generate embedding:', error);
            throw error;
        }
    }

    // Simple FAISS-like implementation for similarity search
    cosineSimilarity(a, b) {
        if (a.length !== b.length) return 0;

        let dotProduct = 0;
        let normA = 0;
        let normB = 0;

        for (let i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        normA = Math.sqrt(normA);
        normB = Math.sqrt(normB);

        if (normA === 0 || normB === 0) return 0;

        return dotProduct / (normA * normB);
    }

    async addToIndex(pageData) {
        try {
            const { content, metadata } = pageData;

            // Check if URL already exists
            const existingIndex = this.findExistingUrl(metadata.url);

            // Generate embedding for the content
            const embedding = await this.generateEmbedding(content);

            const indexEntry = {
                id: existingIndex !== -1 ? this.faissIndex[existingIndex].id : Date.now(),
                embedding: embedding,
                metadata: metadata,
                content: content.substring(0, 1000), // Store first 1000 chars for preview
                timestamp: Date.now()
            };

            if (existingIndex !== -1) {
                // Update existing entry
                this.faissIndex[existingIndex] = indexEntry;
                console.log('RAG Indexer: Updated existing entry for', metadata.url);
            } else {
                // Add new entry
                this.faissIndex.push(indexEntry);
                console.log('RAG Indexer: Added new entry for', metadata.url);
            }

            // Update URL mapping
            this.urlMappings.set(metadata.url, indexEntry.id);

            // Save to storage
            await this.saveStoredData();

            return { success: true, id: indexEntry.id };
        } catch (error) {
            console.error('RAG Indexer: Failed to add to index:', error);
            return { success: false, error: error.message };
        }
    }

    findExistingUrl(url) {
        return this.faissIndex.findIndex(entry => entry.metadata.url === url);
    }

    async searchSimilar(query, topK = 5) {
        if (this.faissIndex.length === 0) {
            return [];
        }

        try {
            const queryEmbedding = await this.generateEmbedding(query);

            // Calculate similarities
            const similarities = this.faissIndex.map((entry, index) => ({
                index,
                similarity: this.cosineSimilarity(queryEmbedding, entry.embedding),
                entry
            }));

            // Sort by similarity and return top K
            return similarities
                .sort((a, b) => b.similarity - a.similarity)
                .slice(0, topK)
                .map(item => ({
                    ...item.entry,
                    similarity: item.similarity
                }));
        } catch (error) {
            console.error('RAG Indexer: Search failed:', error);
            return [];
        }
    }

    getIndexStats() {
        return {
            totalEntries: this.faissIndex.length,
            urlMappings: this.urlMappings.size,
            modelLoaded: this.isModelLoaded
        };
    }

    async clearIndex() {
        this.faissIndex = [];
        this.urlMappings.clear();
        await this.saveStoredData();
        console.log('RAG Indexer: Index cleared');
    }
}

// Initialize the indexer
const ragIndexer = new RAGIndexer();

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    const handleAsync = async () => {
        try {
            switch (request.action) {
                case 'processPage':
                    const result = await ragIndexer.addToIndex(request.data);
                    return result;

                case 'search':
                    const searchResults = await ragIndexer.searchSimilar(request.query, request.topK || 5);
                    return { success: true, results: searchResults };

                case 'getStats':
                    return { success: true, stats: ragIndexer.getIndexStats() };

                case 'clearIndex':
                    await ragIndexer.clearIndex();
                    return { success: true };

                case 'getRecentPages':
                    const recentPages = ragIndexer.faissIndex
                        .sort((a, b) => b.timestamp - a.timestamp)
                        .slice(0, request.limit || 10);
                    return { success: true, pages: recentPages };

                default:
                    return { success: false, error: 'Unknown action' };
            }
        } catch (error) {
            console.error('RAG Indexer: Message handler error:', error);
            return { success: false, error: error.message };
        }
    };

    // Handle async responses
    handleAsync().then(sendResponse);
    return true; // Keep message channel open for async response
});

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
    console.log('RAG Indexer: Extension started');
});

chrome.runtime.onInstalled.addListener(() => {
    console.log('RAG Indexer: Extension installed');
});