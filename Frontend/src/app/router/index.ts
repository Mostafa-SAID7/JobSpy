/**
 * Vue Router configuration for JobSpy
 */

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/features/auth/stores/auth'

// Layout components
import MainLayout from '@/app/layouts/MainLayout.vue'
import AuthLayout from '@/app/layouts/AuthLayout.vue'

// Pages
import HomePage from '@/features/jobs/pages/HomePage.vue'
import JobSearchPage from '@/features/search/pages/JobSearchPage.vue'
import JobDetailsPage from '@/features/jobs/pages/JobDetailsPage.vue'
import SavedJobsPage from '@/features/jobs/pages/SavedJobsPage.vue'
import AlertsPage from '@/features/alerts/pages/AlertsPage.vue'
import ProfilePage from '@/features/profile/pages/ProfilePage.vue'
import LoginPage from '@/features/auth/pages/LoginPage.vue'
import RegisterPage from '@/features/auth/pages/RegisterPage.vue'
import ForgotPasswordPage from '@/features/auth/pages/ForgotPasswordPage.vue'
import NotFoundPage from '@/app/pages/NotFoundPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: HomePage,
      },
      {
        path: 'jobs',
        name: 'JobSearch',
        component: JobSearchPage,
      },
      {
        path: 'jobs/:id',
        name: 'JobDetails',
        component: JobDetailsPage,
      },
      {
        path: 'saved-jobs',
        name: 'SavedJobs',
        component: SavedJobsPage,
        meta: { requiresAuth: true },
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: AlertsPage,
        meta: { requiresAuth: true },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: ProfilePage,
        meta: { requiresAuth: true },
      },
    ],
  },
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: LoginPage,
        meta: { requiresGuest: true },
      },
      {
        path: 'register',
        name: 'Register',
        component: RegisterPage,
        meta: { requiresGuest: true },
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: ForgotPasswordPage,
        meta: { requiresGuest: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Navigation guards
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
