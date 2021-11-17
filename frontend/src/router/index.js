import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Chatroom from "../views/Chatroom.vue"

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/chatroom/:chatroomName',
    name: 'Chatroom',
    props: true,
    component: Chatroom
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
