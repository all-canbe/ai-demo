import { http, HttpResponse, delay } from 'msw'

let mockSessions = [
  {
    id: '1',
    userId: '1',
    title: '产品需求讨论',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
]

let mockMessages = [
  {
    id: '1',
    session_id: '1',
    role: 'user',
    message: '这个产品的核心功能是什么？',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: '2',
    session_id: '1',
    role: 'assistant',
    message: '根据文档分析，产品的核心功能包括用户管理、内容发布、数据分析和系统集成等模块。其中用户管理模块支持多角色权限控制，内容发布支持富文本编辑，数据分析提供实时数据可视化。',
    references: [
      {
        document_id: '1',
        page: 5,
        content: '核心功能模块设计',
      },
    ],
    timestamp: new Date(Date.now() - 86390000).toISOString(),
  },
]

export const chatHandlers = [
  http.get('/api/v1/chat/sessions', async () => {
    await delay(300)

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        items: mockSessions.map((s) => ({
          id: s.id,
          title: s.title,
          created_at: s.created_at,
        })),
        total: mockSessions.length,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    })
  }),

  http.post('/api/v1/chat/sessions', async ({ request }) => {
    await delay(500)

    const body = await request.json() as { document_ids?: string[] }

    const newSession = {
      id: String(mockSessions.length + 1),
      userId: '1',
      title: `新会话 ${mockSessions.length + 1}`,
      created_at: new Date().toISOString(),
    }

    mockSessions.unshift(newSession)

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        id: newSession.id,
        title: newSession.title,
        created_at: newSession.created_at,
      },
    })
  }),

  http.get('/api/v1/chat/:chatId', async ({ params }) => {
    await delay(300)

    const { chatId } = params
    const sessionMessages = mockMessages.filter(
      (msg) => msg.session_id === chatId
    )

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        id: chatId,
        items: sessionMessages.map((m) => ({
          id: m.id,
          role: m.role,
          message: m.message,
          references: m.references || undefined,
          timestamp: m.timestamp,
        })),
        total: sessionMessages.length,
        page: 1,
        page_size: 50,
        total_pages: 1,
      },
    })
  }),

  http.post('/api/v1/chat', async ({ request }) => {
    await delay(1000)

    const body = await request.json() as { message: string; document_ids?: string[]; chat_id?: string }
    const { message, document_ids, chat_id } = body

    const chatId = chat_id || '1'

    const userMessageId = String(mockMessages.length + 1)
    const userMessage = {
      id: userMessageId,
      session_id: chatId,
      role: 'user',
      message: message,
      timestamp: new Date().toISOString(),
    }

    mockMessages.push(userMessage)

    const assistantMessageId = String(mockMessages.length + 1)
    const assistantMessage = {
      id: assistantMessageId,
      session_id: chatId,
      role: 'assistant',
      message: `这是对您问题"${message}"的AI回复。根据文档内容分析，我找到了相关信息。这是一个模拟的回复示例。`,
      references: [
        {
          document_id: document_ids?.[0] || '1',
          page: 3,
          content: '相关章节内容',
        },
      ],
      timestamp: new Date().toISOString(),
    }

    mockMessages.push(assistantMessage)

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        id: assistantMessage.id,
        chat_id: chatId,
        message: assistantMessage.message,
        references: assistantMessage.references,
        timestamp: assistantMessage.timestamp,
      },
    })
  }),

  http.delete('/api/v1/chat/:chatId', async ({ params }) => {
    const { chatId } = params

    await delay(200)

    mockSessions = mockSessions.filter((s) => s.id !== chatId)
    mockMessages = mockMessages.filter((m) => m.session_id !== chatId)

    return HttpResponse.json({
      code: 0,
      message: '聊天会话删除成功',
      data: null,
    })
  }),
]
