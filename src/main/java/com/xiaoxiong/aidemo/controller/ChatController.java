package com.xiaoxiong.aidemo.controller;


import com.xiaoxiong.aidemo.repository.ChatHistoryRepository;
import com.xiaoxiong.aidemo.repository.RedisChatMemory;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import static org.springframework.ai.chat.client.advisor.AbstractChatMemoryAdvisor.CHAT_MEMORY_CONVERSATION_ID_KEY;

@RequiredArgsConstructor
@RestController
@RequestMapping("/ai")
public class ChatController {
    private final ChatHistoryRepository chatHistoryRepository;

    private final ChatClient chatClient;


    private final ChatClient chatClient2;

    private final ChatClient chatClient3;

    private final ChatClient chatClient4;

    private final ChatClient serviceChatClient;



    private final static String PREFIX = "chat:memory:";

    @Autowired
    private RedisChatMemory redisChatMemory;

    @Autowired
    private StringRedisTemplate redisTemplate;



        @RequestMapping(value = "/chat", produces = "text/event-stream")
    public Flux<String> chat(@RequestParam String chatId, @RequestParam String prompt) {

        // 从 chatClient 获取响应内容
        return chatClient.prompt()
                .user(prompt)
                .advisors(a -> a.param("chat_memory_conversation_id_key", chatId))
                .stream()
                .content()
                .doOnNext(s->chatHistoryRepository.save("chat",chatId));
    }

//@RequestMapping(value = "/chat", produces = "text/event-stream")
//public String chat(@RequestParam String chatId, @RequestParam String prompt) {
//    // 构建 QuestionAnswerAdvisor
//    var qaAdvisor = QuestionAnswerAdvisor.builder(vectorStore)
//            .searchRequest(SearchRequest.builder()
//                    .similarityThreshold(0.8d)
//                    .topK(6)
//                    .build())
//            .build();
//
//    // 从 chatClient 获取响应内容
//  ChatResponse chatResponse= ChatClient.builder(ollamaChatModel)//无法判断使用那个模型
//            .build()
//            .prompt()
//            .advisors(qaAdvisor)
//            .user(prompt)
//            .call()
//            .chatResponse();
//    if (chatResponse == null) {
//        // 处理 chatResponse 为 null 的情况，例如抛出异常或提供默认值
//        throw new IllegalStateException("ChatResponse is null");
//    }
//    return chatResponse.toString();
//}



     //"text/html;charset=utf-8"
    @RequestMapping(value = "/chat2Q", produces = "text/event-stream")
    public Flux<String> chat2Q(@RequestParam String chatId,@RequestParam String prompt) {

        return chatClient2.prompt()
                .user(prompt)
                .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, chatId))
                .stream()
                .content()
                .doOnNext(s->chatHistoryRepository.save("chat",chatId))
                .handle((content, sink) -> {
                    // 将content以string的形式存入redis
                    String redisKey = PREFIX + chatId;
                    String currentValue = redisTemplate.opsForValue().get(redisKey);
                    String updatedValue = currentValue != null ? currentValue + content : content;
                    redisTemplate.opsForValue().set(redisKey, updatedValue);
                    sink.next(content.replace("*", ""));
                });
    }

    @RequestMapping(value = "/chat2D", produces = "text/event-stream")
    public Flux<String> chat2D(@RequestParam String chatId,@RequestParam String prompt) {
        return chatClient3.prompt()
                .user(prompt)
                .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, chatId))
                .stream()
                .content()
                .doOnNext(s->chatHistoryRepository.save("chat",chatId))
                .handle((content, sink) -> {
                    // 将content以string的形式存入redis
                    String redisKey = PREFIX + chatId;
                    String currentValue = redisTemplate.opsForValue().get(redisKey);
                    String updatedValue = currentValue != null ? currentValue + content : content;
                    redisTemplate.opsForValue().set(redisKey, updatedValue);
                    sink.next(content.replace("*", ""));
                });
    }

    @RequestMapping(value = "/chat2F", produces = "text/event-stream")
    public Flux<String> chat2F(@RequestParam String chatId,@RequestParam String prompt) {
        return chatClient4.prompt()
                .user(prompt)
                .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, chatId))
                .stream()
                .content()
                .doOnNext(s->chatHistoryRepository.save("chat",chatId))
                .handle((content, sink) -> {
                    // 将content以string的形式存入redis
                    String redisKey = PREFIX + chatId;
                    String currentValue = redisTemplate.opsForValue().get(redisKey);
                    String updatedValue = currentValue != null ? currentValue + content : content;
                    redisTemplate.opsForValue().set(redisKey, updatedValue);
                    sink.next(content.replace("*", ""));
                });
    }

    @RequestMapping(value = "/service", produces = "text/event-stream")
    public String service( String chatId, String prompt) {
        // 1.保存会话id
        chatHistoryRepository.save("service", chatId);
        // 2.请求模型
        return serviceChatClient.prompt()
                .user(prompt)
                .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, chatId))
                .call()
                .content();
    }


}
