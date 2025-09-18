import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/demo/HomeView.vue'
import History from '../views/question/HistoryView.vue'
import Create from '../views/question/CreateView.vue'
import Groups from '../views/group/GroupsView.vue'
import Quiz from '../views/user/QuizView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/questions/history',
      name: 'questionHistory',
      component: History,
    },
    {
      path: '/questions/create',
      name: 'createQuestion',
      component: Create,
    },
    {
      path: '/groups',
      name: 'groupManagement',
      component: Groups,
    },
    {
      path: '/admin/quiz',
      name: 'admin-quiz-management',
      // route level code-splitting
      // this generates a separate chunk for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/admin/QuizManagementView.vue'),
    },
    {
      path: '/admin/quiz/:id',
      name: 'admin-quiz-detail',
      // route level code-splitting
      // this generates a separate chunk for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/admin/QuizDetailView.vue'),
      props: true,
    },
    {
      path: '/results',
      name: 'results',
      // route level code-splitting
      component: () => import('../views/user/ResultsView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      component: () => import('../views/common/AboutView.vue'),
    },
    {
      path: '/quiz/list',
      name: 'Quiz',
      component: Quiz,
    },
  ],
})

export default router
