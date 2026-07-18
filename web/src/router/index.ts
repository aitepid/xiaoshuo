import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: '小说广场' },
    },
    {
      path: '/auth/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: '登录' },
    },
    {
      path: '/auth/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { title: '注册' },
    },
    {
      path: '/bookshelf',
      name: 'bookshelf',
      component: () => import('@/views/BookshelfView.vue'),
      meta: { title: '我的书架', requiresAuth: true },
    },
    {
      path: '/creator',
      name: 'creator',
      component: () => import('@/views/CreatorCenterView.vue'),
      meta: { title: '创作中心', requiresAuth: true },
    },
    {
      path: '/reader/:novelId/:chapterId?',
      name: 'reader',
      component: () => import('@/views/ReaderView.vue'),
      meta: { title: '阅读器' },
    },
    {
      path: '/novels/:id',
      name: 'novel-detail',
      component: () => import('@/views/NovelDetailView.vue'),
      meta: { title: '书籍详情' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { title: '页面未找到' },
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  authStore.bootFromStorage()

  if (to.meta.title) {
    document.title = `${to.meta.title} | 晨昏书局`
  }

  if (!to.meta.requiresAuth) {
    return true
  }

  if (authStore.isAuthenticated) {
    await authStore.loadProfile().catch(() => undefined)
    return true
  }

  const refreshed = await authStore.refreshSession()
  if (refreshed) {
    await authStore.loadProfile().catch(() => undefined)
    return true
  }

  return {
    name: 'login',
    query: {
      redirect: to.fullPath,
    },
  }
})

export default router
