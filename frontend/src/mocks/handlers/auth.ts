import { http, HttpResponse } from 'msw'

const mockUsers = [
  {
    id: '1',
    email: 'demo@example.com',
    password: 'demo123',
    name: '演示用户',
  },
]

export const authHandlers = [
  http.post('/api/v1/auth/login', async ({ request }) => {
    const { email, password } = await request.json()
    
    const user = mockUsers.find(
      (u) => u.email === email && u.password === password
    )

    if (!user) {
      return HttpResponse.json(
        { code: 401, message: '邮箱或密码错误', data: null },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      code: 0,
      message: '登录成功',
      data: {
        access_token: 'mock-access-token-' + Date.now(),
        refresh_token: 'mock-refresh-token-' + Date.now(),
        token_type: 'bearer',
        expires_in: 3600,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
        },
      },
    })
  }),

  http.post('/api/v1/auth/register', async ({ request }) => {
    const { email, password, name } = await request.json()
    
    const existingUser = mockUsers.find((u) => u.email === email)
    if (existingUser) {
      return HttpResponse.json(
        { code: 400, message: '邮箱已被注册', data: null },
        { status: 400 }
      )
    }

    const newUser = {
      id: String(mockUsers.length + 1),
      email,
      password,
      name,
    }
    mockUsers.push(newUser)

    return HttpResponse.json({
      code: 0,
      message: '注册成功',
      data: {
        access_token: 'mock-access-token-' + Date.now(),
        refresh_token: 'mock-refresh-token-' + Date.now(),
        token_type: 'bearer',
        expires_in: 3600,
        user: {
          id: newUser.id,
          email: newUser.email,
          name: newUser.name,
        },
      },
    })
  }),

  http.post('/api/v1/auth/logout', () => {
    return HttpResponse.json({
      code: 0,
      message: '登出成功',
      data: null,
    })
  }),

  http.post('/api/v1/auth/refresh', async ({ request }) => {
    const { refreshToken } = await request.json()

    if (!refreshToken) {
      return HttpResponse.json(
        { code: 1006, message: '无效的刷新令牌', data: null },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      code: 0,
      message: '刷新成功',
      data: {
        access_token: 'mock-access-token-' + Date.now(),
        token_type: 'bearer',
        expires_in: 3600,
      },
    })
  }),

  http.get('/api/v1/auth/me', async ({ request }) => {
    const authHeader = request.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        { code: 1001, message: '未登录，请先登录', data: null },
        { status: 401 }
      )
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        id: '1',
        email: 'demo@example.com',
        name: '演示用户',
        created_at: new Date().toISOString(),
      },
    })
  }),
]
