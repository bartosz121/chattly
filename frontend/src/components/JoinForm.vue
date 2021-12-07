<template>
  <div class="w-full max-w-xs md:max-w-lg">
    <form @submit="onSubmit" class="bg-blue-50 shadow-md rounded px-8 pt-6 pb-8 mb-4">
      <div class="mb-4">
        <label class="block text-center text-gray-700 font-bold mb-2 select-none" for="username">
          Username
        </label>
        <input v-model="username" class="w-full py-2 px-3 text-gray-700 leading-tight shadow border rounded pr-2 focus:outline-none" type="text" name="username" maxlength="12" autocomplete="off">
      </div>
      <div class="mb-6">
        <label class="block text-center text-gray-700 font-bold mb-2 select-none" for="chatroom-name">
          Chatroom
        </label>
        <div class="flex flex-row w-full bg-white shadow border rounded pr-2">
          <input v-model="chatroomName" class="w-11/12 py-2 px-3 text-gray-700 leading-tight rounded focus:outline-none" type="text" name="username" maxlength="36" autocomplete="off">
          <div @click="randomChatroom" class="icon">
            <dice-icon class="h-full hover-cursor text-gray-700 hover:text-black" size="24" />
          </div>
        </div>
      </div>
      <Button extendStyle="font-bold w-full select-none" type="submit">Join</Button>
    </form>
  </div>
</template>

<script>
  import { v4 as uuidv4 } from 'uuid'
  import { DiceIcon } from 'vue-tabler-icons'
  import Button from '@/components/Button.vue'

  export default {
    name: 'JoinForm',
    components: {
      DiceIcon,
      Button,
    },
    data() {
      return {
        username: '',
        chatroomName: '',
        examples: {
          chatrooms: ['general', 'study', 'league-of-legends', 'programming', 'football',
            'nba', 'music', 'politics', 'random-talk', 'stock-market', 'crypto', 'ctf',
            'tv-shows', 'movies', 'mensa', 'cats',],
        },
      }
    },
    created(){
      // Add some random strings to examples
      for(let i = 0; i < 5; i++){
        this.examples.chatrooms.push(uuidv4())
      }
    },
    mounted(){
      this.chatroomName = this.$route.query.chatroom
    },
    methods: {
      randomChatroom() {
        const chatRooms = this.examples.chatrooms
        this.chatroomName = chatRooms[Math.floor(Math.random() * chatRooms.length)]
      },
      onSubmit(e) {
        e.preventDefault()
        if(!this.username || !this.chatroomName){
          alert("Please enter username and chatroom")
        }else{
          this.$router.push({
            name: 'Chatroom',
            params: {
              username: this.username,
              chatroomName: this.chatroomName
            }
          })
        }
      }
    },
  }
</script>