package com.xiaoxiong.aidemo.repository;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.messages.Message;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

@Component
public class RedisChatMemory implements ChatMemory {

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    @Autowired
    public RedisChatMemory(StringRedisTemplate redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    private final static String PREFIX = "chat:memory:";


    @Override
    public void add(String chatId, List<Message> messages) {
        String key = PREFIX + chatId;
        messages.forEach(msg -> {
            try {
                String json = objectMapper.writeValueAsString(msg);
                redisTemplate.opsForList().rightPush(key, json);
            } catch (JsonProcessingException e) {
                // 处理异常
            }
        });
    }
    @Override
    public List<Message> get(String conversationId, int lastN) {
        String key = PREFIX + conversationId;
        List<String> jsonList = redisTemplate.opsForList().range(key, 0, lastN);
        List<Message> collect = jsonList.stream()
                // 对每个json进行处理，转换为Message对象
                .map(json -> {
                    try {
                        // 使用objectMapper将json转换为Message对象
                        return objectMapper.readValue(json, Message.class);
                    } catch (Exception e) {
                        // 处理异常
//                        throw new RuntimeException("Failed to deserialize JSON to Message", e);
                        return null;
                    }
                })
                // 过滤掉为null的Message对象
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
        return collect;
    }

    @Override
    public void clear(String conversationId) {
        redisTemplate.delete(PREFIX + conversationId);
    }
}