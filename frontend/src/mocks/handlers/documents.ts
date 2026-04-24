import { http, HttpResponse, delay } from 'msw'

let mockDocuments = [
  {
    id: '1',
    userId: '1',
    name: '产品需求文档.pdf',
    type: 'pdf',
    size: 1024000,
    fileUrl: '/api/v1/documents/1/download',
    processingStatus: 'completed',
    uploadTime: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: '2',
    userId: '1',
    name: '技术架构设计.docx',
    type: 'docx',
    size: 512000,
    fileUrl: '/api/v1/documents/2/download',
    processingStatus: 'completed',
    uploadTime: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: '3',
    userId: '1',
    name: '项目计划.xlsx',
    type: 'xlsx',
    size: 256000,
    fileUrl: '/api/v1/documents/3/download',
    processingStatus: 'embedding',
    uploadTime: new Date(Date.now() - 259200000).toISOString(),
  },
  {
    id: '4',
    userId: '1',
    name: '会议纪要.txt',
    type: 'txt',
    size: 10240,
    fileUrl: '/api/v1/documents/4/download',
    processingStatus: 'failed',
    uploadTime: new Date(Date.now() - 345600000).toISOString(),
  },
]

export const documentsHandlers = [
  http.get('/api/v1/documents', async ({ request }) => {
    const url = new URL(request.url)
    const folderId = url.searchParams.get('folderId')

    await delay(300)

    let filteredDocuments = mockDocuments
    if (folderId) {
      filteredDocuments = mockDocuments.filter((doc) => doc.folderId === folderId)
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        items: filteredDocuments,
        total: filteredDocuments.length,
        page: 1,
        page_size: 20,
        total_pages: 1,
      },
    })
  }),

  http.post('/api/v1/documents', async ({ request }) => {
    await delay(1000)

    const formData = await request.formData()
    const file = formData.get('file') as File
    const folderId = formData.get('folder_id') as string | null

    const newDocument = {
      id: String(mockDocuments.length + 1),
      userId: '1',
      folderId: folderId || undefined,
      name: file.name,
      type: file.name.split('.').pop() || '',
      size: file.size,
      fileUrl: `/api/v1/documents/${mockDocuments.length + 1}/download`,
      processingStatus: 'pending',
      uploadTime: new Date().toISOString(),
    }

    mockDocuments.unshift(newDocument)

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: newDocument,
    })
  }),

  http.delete('/api/v1/documents/:id', async ({ params }) => {
    const { id } = params

    await delay(200)

    mockDocuments = mockDocuments.filter((doc) => doc.id !== id)

    return HttpResponse.json({
      code: 0,
      message: '文档删除成功',
      data: null,
    })
  }),

  http.get('/api/v1/documents/:id/summary', async ({ params }) => {
    await delay(500)

    const { id } = params
    const document = mockDocuments.find((doc) => doc.id === id)

    if (!document) {
      return HttpResponse.json(
        { code: 3003, message: '文档不存在', data: null },
        { status: 404 }
      )
    }

    const summaries: Record<string, { document_id: string; summary: string; key_points: string[] }> = {
      '1': {
        document_id: '1',
        summary: '本文档详细描述了产品的功能需求和技术规范，包括用户界面设计、系统架构、性能要求等关键内容',
        key_points: [
          '产品目标用户定位清晰',
          '功能模块划分合理',
          '技术架构设计先进',
          '性能指标要求明确',
        ],
      },
      '2': {
        document_id: '2',
        summary: '技术架构设计文档阐述了系统的整体架构、技术选型和系统安全策略',
        key_points: [
          '采用微服务架构设计',
          '使用Docker容器化部署',
          '数据库采用PostgreSQL',
          '缓存使用Redis',
        ],
      },
    }

    const defaultSummary = {
      document_id: id as string,
      summary: '文档内容正在分析中，请稍后再试',
      key_points: [],
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: summaries[id as string] || defaultSummary,
    })
  }),

  http.get('/api/v1/documents/:id/status', async ({ params }) => {
    await delay(200)

    const { id } = params
    const document = mockDocuments.find((doc) => doc.id === id)

    if (!document) {
      return HttpResponse.json(
        { code: 3003, message: '文档不存在', data: null },
        { status: 404 }
      )
    }

    const progressMap: Record<string, number> = {
      pending: 0,
      parsing: 25,
      extracting: 50,
      embedding: 75,
      completed: 100,
      failed: 0,
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        id: document.id,
        processing_status: document.processingStatus,
        progress: progressMap[document.processingStatus] || 0,
        error_message: document.processingStatus === 'failed' ? '解析失败' : null,
        updated_at: new Date().toISOString(),
      },
    })
  }),
]
