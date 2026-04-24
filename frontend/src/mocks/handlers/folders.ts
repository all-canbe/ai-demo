import { http, HttpResponse, delay } from 'msw'

let mockFolders = [
  {
    id: '1',
    userId: '1',
    name: '工作文档',
    parentId: undefined,
    createdAt: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: '2',
    userId: '1',
    name: '学习资料',
    parentId: undefined,
    createdAt: new Date(Date.now() - 172800000).toISOString(),
  },
  {
    id: '3',
    userId: '1',
    name: '项目资料',
    parentId: '1',
    createdAt: new Date(Date.now() - 259200000).toISOString(),
  },
]

export const foldersHandlers = [
  http.get('/api/v1/folders', async () => {
    await delay(300)
    
    return HttpResponse.json({
      code: 0,
      message: '获取成功',
      data: mockFolders,
    })
  }),

  http.post('/api/v1/folders', async ({ request }) => {
    await delay(300)
    
    const { name, parentId } = await request.json()
    
    const newFolder = {
      id: String(mockFolders.length + 1),
      userId: '1',
      name,
      parentId: parentId || undefined,
      createdAt: new Date().toISOString(),
    }
    
    mockFolders.push(newFolder)

    return HttpResponse.json({
      code: 0,
      message: '创建成功',
      data: newFolder,
    })
  }),

  http.delete('/api/v1/folders/:id', async ({ params }) => {
    const { id } = params
    
    await delay(200)
    
    mockFolders = mockFolders.filter((folder) => folder.id !== id)

    return HttpResponse.json({
      code: 0,
      message: '删除成功',
      data: null,
    })
  }),
]
