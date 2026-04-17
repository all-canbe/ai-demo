package com.xiaoxiong.aidemo.config;


import com.xiaoxiong.aidemo.tools.CourseTools;
import com.xiaoxiong.aidemo.repository.RedisChatMemory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.client.advisor.SimpleLoggerAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static com.xiaoxiong.aidemo.constants.SystemConstants.CUSTOMER_SERVICE_SYSTEM;

@Configuration
public class CommonConfig {
    @Autowired
    private OpenAiConfig openAiConfig;

    @Bean
    public ChatClient chatClient(OllamaChatModel  model, ChatMemory redisChatMemory) {
        return ChatClient
                .builder(model)
                .defaultSystem("你是一个活泼的智能助手，你叫小熊，请以小熊的身份和语气回复")
                .defaultAdvisors(new SimpleLoggerAdvisor(),
                        new MessageChatMemoryAdvisor(redisChatMemory))
                .build();
    }

    @Bean
    public ChatClient chatClient2(OpenAiChatModel model, ChatMemory redisChatMemory) {
        return ChatClient
                .builder(model)
                .defaultSystem("你是一个专业的ai助手，请以专业严肃的语气回复")
                .defaultAdvisors(new SimpleLoggerAdvisor(),
                        new MessageChatMemoryAdvisor(redisChatMemory))
                .build();
    }

    @Bean
    public ChatClient chatClient3(ChatMemory redisChatMemory) {
        return ChatClient
                .builder(openAiConfig.getmodel(0))
                .defaultSystem("你是一个可爱的ai助手，请以可爱活力的语气回复")
                .defaultAdvisors(new SimpleLoggerAdvisor(),
                        new MessageChatMemoryAdvisor(redisChatMemory))
                .build();
    }
    @Bean
    public ChatClient chatClient4(ChatMemory redisChatMemory) {
        return ChatClient
                .builder(openAiConfig.getmodel(1))
                .defaultSystem("你是一个专业的法律顾问，请以正式专业的语气回复")
                .defaultAdvisors(new SimpleLoggerAdvisor(),
                        new MessageChatMemoryAdvisor(redisChatMemory))
                .build();
    }

    @Bean
    public ChatClient serviceChatClient(
            ChatMemory redisChatMemory,
            CourseTools courseTools) {
        return ChatClient.builder(openAiConfig.getmodel(1))
                .defaultSystem(CUSTOMER_SERVICE_SYSTEM)
                .defaultAdvisors(
                        new MessageChatMemoryAdvisor(redisChatMemory),
                        new SimpleLoggerAdvisor())
                .defaultTools(courseTools)
                .build();
    }

}
