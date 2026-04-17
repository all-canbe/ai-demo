package com.xiaoxiong.aidemo.tools;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.VectorStore;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class DocumentProcessor {

    private final VectorStore vectorStore;

    public DocumentProcessor(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    public void addDocumentToVectorStore(String filePath) {
        File documentation = new File(filePath);
        List<Document> documents = new ArrayList<>();

        try {
            PDDocument document = PDDocument.load(documentation);
            PDFTextStripper pdfTextStripper = new PDFTextStripper();
            String content = pdfTextStripper.getText(document);

            // 自定义文本分割逻辑
            List<String> chunks = splitTextIntoChunks(content, 300, 200, 10, 400);

            for (String chunk : chunks) {
                documents.add(new Document(chunk));
            }

            document.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        documents.forEach(document -> vectorStore.add(List.of(document)));
    }

    private List<String> splitTextIntoChunks(String text, int maxChunkSize, int minChunkSize, int chunkOverlap, int chunkSize) {
        List<String> chunks = new ArrayList<>();
        int textLength = text.length();
        int chunkSizeWithOverlap = chunkSize + chunkOverlap;

        for (int start = 0; start < textLength; start += chunkSizeWithOverlap) {
            int end = Math.min(start + maxChunkSize, textLength);
            int actualChunkSize = Math.min(chunkSize, end - start);
            String chunk = text.substring(start, start + actualChunkSize);
            chunks.add(chunk);
        }

        return chunks;
    }
}