<template>
  <div
    ref="msg"
    class="
      chat-msg
      my-2
      w-95/100
      border-2
      rounded-2xl
      shadow-lg
      bg-blue-200
      border-transparent
      bg-opacity-70
    "
  >
    <div class="block break-all p-3 text-sm antialiased">
      <span
        class="text-xs text-gray-400 mr-1"
        :title="dtToLocaleString(dt, 'full-date')"
        >{{ dtToLocaleString(dt) }}</span
      >
      <span
        class="font-semibold"
        :class="
          author.toLowerCase() === 'admin'
            ? 'text-red-600 font-bold underline'
            : null
        "
        >{{ author }}</span
      >: {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  name: "ChatMessage",
  props: {
    dt: {
      type: Number,
    },
    author: {
      type: String,
    },
    message: {
      type: String,
    },
  },
  setup() {
    const msg = ref(null);

    onMounted(() => {
      msg.value.scrollIntoView();
    });

    return {
      msg,
    };
  },
  methods: {
    dtToLocaleString(unix, format = "short") {
      let options = {
        hour: "2-digit",
        minute: "2-digit",
      };

      switch (format) {
        case "short":
          break;
        case "full-time":
          options = {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          };
          break;

        case "full-date":
          options = {
            year: "numeric",
            month: "numeric",
            day: "numeric",
            hour: "numeric",
            minute: "numeric",
            second: "numeric",
            timeZoneName: "long",
          };
          break;

        default:
          break;
      }
      const date = new Date(unix);
      return new Intl.DateTimeFormat([], options).format(date);
    },
  },
};
</script>