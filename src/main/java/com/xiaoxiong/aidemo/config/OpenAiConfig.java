package com.xiaoxiong.aidemo.config;

import com.openai.client.OpenAIClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.ArrayList;
import java.util.List;


@Configuration
public class OpenAiConfig {

    @Value("${spring.ai.openai.api-key}")
    private String apiKey;

    @Value("${spring.ai.openai.base-url}")
    private String baseUrl;

    @Bean
    public OpenAiApi openAiApi() {
        return OpenAiApi.builder()
                .baseUrl(baseUrl)
                .apiKey(apiKey)
                .build();
    }
    public  OpenAiChatModel getmodel(int no){
        List<OpenAiChatModel> chatModels = models(openAiApi());
        return chatModels.get(no);
    }



    public List<OpenAiChatModel> models(OpenAiApi openAiApi) {
        List<OpenAiChatModel> chatModels = new ArrayList<>();
        chatModels.add(chat2(openAiApi));
        chatModels.add(chat3(openAiApi));
        return chatModels;
    }

    public OpenAiChatModel chat2(OpenAiApi openAiApi) {
        // 配置 OpenAiChatOptions
        OpenAiChatOptions options = OpenAiChatOptions.builder()
                .model("deepseek-r1-0528") // 设置使用的模型
                .temperature(0.7) // 设置采样温度
                .maxTokens(200) // 设置最大生成令牌数
                .build();

        // 创建并返回 OpenAiChatModel 实例
        return new OpenAiChatModel(openAiApi, options);
    }


    //qwen-plus-character

    public OpenAiChatModel chat3(OpenAiApi openAiApi) {
        // 配置 OpenAiChatOptions
        OpenAiChatOptions options = OpenAiChatOptions.builder()
                .model("qwen-plus-character") // 设置使用的模型
                .temperature(0.6) // 设置采样温度
                .maxTokens(500) // 设置最大生成令牌数
                .build();

        // 创建并返回 OpenAiChatModel 实例
        return new OpenAiChatModel(openAiApi, options);
    }
}