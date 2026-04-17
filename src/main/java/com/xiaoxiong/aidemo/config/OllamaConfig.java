package com.xiaoxiong.aidemo.config;

import io.micrometer.observation.ObservationRegistry;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.ollama.OllamaEmbeddingModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.ai.ollama.management.ModelManagementOptions;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class OllamaConfig {

    @Bean
    @Primary
    public EmbeddingModel ollamaEmbeddingModel1() {
        return new OllamaEmbeddingModel(new OllamaApi(), defaultOllamaOptions(), observationRegistry(),modelManagementOptions());
    }



    @Bean
    public OllamaOptions defaultOllamaOptions() {
        return OllamaOptions.builder()
                .model("nomic-embed-text")
                .build();
    }

    @Bean
    public ModelManagementOptions modelManagementOptions() {
        return ModelManagementOptions.builder()
                .build();
    }

    // 如果你需要使用ObservationRegistry，可以像下面这样注入
    public ObservationRegistry observationRegistry() {
        // 使用observationRegistry进行观测配置
        return ObservationRegistry.create();
    }
}