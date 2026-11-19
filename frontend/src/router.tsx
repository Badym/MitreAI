import { createBrowserRouter } from 'react-router'
import { RequireAuth } from './components/auth/RequireAuth'
import { AppLayout } from './components/layout/AppLayout'
import { ChatPage } from './pages/ChatPage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <ChatPage /> },
      { path: 'c/:conversationId', element: <ChatPage /> },
    ],
  },
  { path: '/login', element: <LoginPage /> },
  { path: '*', element: <NotFoundPage /> },
])
