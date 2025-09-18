import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/demo/HomeView.vue'
import History from '../views/question/HistoryView.vue'
import Create from '../views/question/CreateView.vue'
import Groups from '../views/group/GroupsView.vue'

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
  ],
})

export default router
