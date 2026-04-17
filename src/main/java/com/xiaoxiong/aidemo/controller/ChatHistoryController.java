package com.xiaoxiong.aidemo.controller;

import com.xiaoxiong.aidemo.repository.ChatHistoryRepository;
import com.xiaoxiong.aidemo.repository.RedisChatMemory;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.messages.Message;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;


@RestController
@RequestMapping("/ai/history")
public class ChatHistoryController {

    @Autowired
    private  ChatMemory chatMemory;

    @Autowired
    private RedisChatMemory redisTChatMemory;

    @Autowired
    private ChatHistoryRepository chatHistoryRepository;


    /**
     * 查询会话历史列表
     * @param type 业务类型，如：chat,service,pdf
     * @return chatId列表
     */
    @GetMapping("/{type}")
    public List<String> getChatIds(@PathVariable("type") String type) {
        return chatHistoryRepository.getChatIds(type);
    }

    /**
     * 根据业务类型、chatId查询会话历史
     * @param type 业务类型，如：chat,service,pdf
     * @param chatId 会话id
     * @return 指定会话的历史消息
     */
    @GetMapping("/{type}/{chatId}")
    public  List<Message> getChatHistory(@PathVariable("type") String type, @PathVariable("chatId") String chatId) {
        List<Message> messages = redisTChatMemory.get(chatId, -1);
//        MessageVO messageVO = new MessageVO(messages);
//        messageVO.setRole("ASSISTANT");

        return messages;
    }
}