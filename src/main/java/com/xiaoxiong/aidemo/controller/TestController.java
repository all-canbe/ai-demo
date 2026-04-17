package com.xiaoxiong.aidemo.controller;


import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/test")
public class TestController {

    private final ChatClient chatClient;
    private VectorStore vectorStore;

    public TestController(ChatClient chatClient) {
        this.chatClient = chatClient;
    }


    @GetMapping("/chat")
    public String chat(String message) {
        // 定义提示词模版
        String template="你是一个智能助手，你可以根据下面搜索到的内容回复用户，如果搜索不到酌情回复";

        PromptTemplate customPromptTemplate = new PromptTemplate(template);



        QuestionAnswerAdvisor qaAdvisor = QuestionAnswerAdvisor.builder(vectorStore)
                // 设置提示词模版对象，如果不设置，使用默认的模版
                .promptTemplate(customPromptTemplate)
                // 指定进行向量搜索时的基本条件
                .searchRequest(SearchRequest.builder().topK(3).similarityThreshold(0.5).build())
                .build();

        ChatResponse chatResponse = chatClient.prompt()
                .advisors(qaAdvisor)
                .user(message)
                .call()
                .chatResponse();
        System.out.println(chatResponse.getResult().getOutput().getText());
        return "success";
    }
}
