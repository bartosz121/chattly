<template>
  <div class="hero w-full h-4/6 md:h-full flex flex-col">
    <div
      class="
        peers-feed
        flex flex-row flex-wrap
        gap-2
        justify-evenly
        overflow-hidden
        h-4/6
        md:h-3/4
        mx-2
        my-4
        md:ml-8
        bg-white
        rounded-xl
        bg-opacity-60
        backdrop-filter backdrop-blur-lg
      "
      :key="rerenderKey"
    >
      <div
        class="w-40 md:w-48 xl:w-64 peer-feed flex-shrink"
        v-for="peer in visiblePeers"
        :key="peer.peerUsername"
      >
        <PeerStream :peerObj="peer" />
      </div>
    </div>
    <div
      class="
        local-feed
        h-2/6
        md:h-1/4
        mx-2
        md:ml-8
        bg-white
        rounded-xl
        bg-opacity-60
        backdrop-filter backdrop-blur-lg
      "
    >
      <div class="h-full" v-if="this.localStream.mediaStream">
        <div
          class="
            flex
            p-4
            h-full
            flex-row
            md:justify-evenly
            items-center
            gap-2
            md:gap-24
          "
        >
          <div class="h-full flex flex-row items-center gap-10">
            <video
              class="h-full"
              :srcObject="this.localStream.mediaStream"
              muted
              autoplay
              playsinline
            ></video>
            <div class="local-switches flex flex-col">
              <div class="flex flex-row">
                <video-icon size="24" />
                <ToggleSwitch
                  @toggle-switch="toggleLocalTrack($event, 'video')"
                  :initBool="this.localStream.flags.video"
                />
              </div>
              <div class="flex flex-row">
                <microphone-icon size="24" />
                <ToggleSwitch
                  @toggle-switch="toggleLocalTrack($event, 'audio')"
                  :initBool="this.localStream.flags.audio"
                />
              </div>
              <p class="text-center select-none">{{ this.username }}</p>
            </div>
          </div>
          <!-- <div class="invisible md:visible screen-share border-1 border-red-400">
            <h2>SCREEN SHARE TODO</h2>
          </div> -->
        </div>
      </div>
      <div class="h-full flex flex-row justify-center items-center" v-else>
        <p class="text-lg">Waiting for user media permission...</p>
      </div>
    </div>
  </div>
  <div class="w-full flex-shrink-0 h-2/6 md:h-95/100 md:w-80">
    <div
      class="
        chat
        flex-col
        mx-2
        md:mx-4
        h-full
        bg-white
        p-5
        rounded-xl
        bg-opacity-60
        backdrop-filter backdrop-blur-lg
      "
    >
      <div
        class="
          chatroom-info
          border-b-2 border-gray-500 border-opacity-25
          h-1/6
          md:h-1/10
          flex flex-row
          justify-around
          items-center
        "
      >
        <span class="truncate" :title="chatroomName">{{ chatroomName }}</span>
        <div class="flex flex-row whitespace-nowrap" :key="rerenderKey">
          <users-icon size="24" />{{ this.getPeerCount() }}
        </div>
      </div>
      <div
        class="
          msg-list
          overflow-x-hidden
          flex flex-col
          my-3
          h-1/2
          md:h-5/6
          scrollbar-thin scrollbar-thumb-sky-300 scrollbar-track-sky-200
        "
      >
        <ChatMessage
          v-for="(msg, index) in chat.messages"
          :key="index"
          :dt="msg.dt"
          :author="msg.author"
          :message="msg.message"
        />
      </div>
      <div class="input-box h-auto flex flex-row items-center justify-around">
        <input
          @keyup.enter="sendChatMessage"
          v-model="chat.msgInput"
          class="
            w-10/12
            h-10
            md:h-auto md:w-8/12
            py-2
            px-3
            text-gray-700
            leading-tight
            rounded
            focus:outline-none
            resize-none
          "
          type="text"
          maxlength="255"
        />
        <Button @btn-click="sendChatMessage" sizing="py-1.5 px-4 rounded"
          >Send</Button
        >
      </div>
    </div>
  </div>
</template>

<script>
import { useWindowSize } from "vue-window-size";
import { UsersIcon, VideoIcon, MicrophoneIcon } from "vue-tabler-icons";
import Button from "@/components/Button";
import ToggleSwitch from "@/components/ToggleSwitch.vue";
import PeerStream from "@/components/PeerStream.vue";
import ChatMessage from "@/components/ChatMessage.vue";

export default {
  name: "Chatroom",
  props: {
    username: String,
    chatroomName: String,
  },
  components: {
    UsersIcon,
    VideoIcon,
    MicrophoneIcon,
    Button,
    ToggleSwitch,
    PeerStream,
    ChatMessage,
  },
  setup() {
    const { width, height } = useWindowSize();
    return {
      windowWidth: width,
      windowHeight: height,
    };
  },
  data() {
    return {
      rerenderKey: 0, // used to force rerender
      websocket: null,
      connectedPeers: {},
      chat: {
        messages: [
          {
            dt: Date.now(),
            author: "Admin",
            message: `Welcome to "${this.chatroomName}"!`,
          },
        ],
        msgInput: "",
      },
      localStream: {
        mediaStream: null,
        tracks: {
          audio: null,
          video: null,
        },
        flags: {
          audio: false,
          video: false,
        },
        constraints: {
          video: true,
          audio: true,
        },
      },
      config: {
        iceServers: [
          {
            urls: [
              "stun:stun1.l.google.com:19302",
              "stun:stun2.l.google.com:19302",
            ],
          },
        ],
        iceCandidatePoolSize: 10,
      },
    };
  },
  async beforeMount() {
    // there could be no username if user enters chatroom through url;
    // also do not allow 'admin' as username
    // if that happens redirect to home with chatroom name as query parameter
    if (!this.username || this.username.toLowerCase() === "admin") {
      this.$router.push({
        name: "Home",
        query: {
          chatroom: this.chatroomName.slice(0, 36),
        },
      });
    } else {
      // Create websocket if all good
      await this.getUserMedia();
      this.createWebsocket();
    }
  },
  computed: {
    // TODO maybe pass array with remote streams instead of object with all peers data
    visiblePeers() {
      const maxPeerStreams = this.maxPeerStreams();

      const allPeers = this.getAllPeers();

      const maxVisiblePeers = Object.fromEntries(
        Object.entries(allPeers).slice(0, maxPeerStreams)
      );

      return maxVisiblePeers;
    },
  },
  methods: {
    forceRerender() {
      this.rerenderKey += 1;
    },

    addPeer(peerName, peer, peerDataChannel, remoteStream) {
      if (this.username === peerName) {
        this.username = "usernameTaken";
      }
      this.connectedPeers[peerName] = {
        peer,
        peerName,
        peerDataChannel,
        remoteStream,
      };
      this.forceRerender();
    },

    removePeer(peerName) {
      delete this.connectedPeers[peerName];
      this.forceRerender();
    },

    getPeer(peerName) {
      return this.connectedPeers[peerName];
    },

    getAllPeers() {
      return this.connectedPeers;
    },

    getDataChannels() {
      let dataChannels = [];
      for (let peerName in this.connectedPeers) {
        dataChannels.push(this.connectedPeers[peerName].peerDataChannel);
      }

      return dataChannels;
    },

    getPeerCount() {
      return Object.keys(this.connectedPeers).length + 1;
    },

    // FIXME find better way to do this
    // right now these values are from trial and error
    maxPeerStreams() {
      if (0 < this.windowWidth && this.windowWidth < 512) {
        return 4;
      } else if (512 <= this.windowWidth && this.windowWidth < 680) {
        return 6;
      } else if (680 <= this.windowWidth && this.windowWidth < 1176) {
        return 8;
      } else if (1176 <= this.windowWidth && this.windowWidth < 1280) {
        return 12;
      } else if (1280 <= this.windowWidth && this.windowWidth < 1432) {
        return 6;
      } else if (1432 <= this.windowWidth && this.windowWidth < 1700) {
        return 12;
      } else if (this.windowWidth >= 1700) {
        return 16;
      } else {
        return 4;
      }
    },

    async getUserMedia() {
      await navigator.mediaDevices
        .getUserMedia(this.localStream.constraints)
        .then((stream) => {
          this.localStream.mediaStream = stream;

          this.localStream.tracks.audio = stream.getAudioTracks();
          this.localStream.tracks.video = stream.getVideoTracks();

          this.localStream.tracks.audio[0].enabled = false;
          this.localStream.tracks.video[0].enabled = false;
        })
        .catch((error) => {
          console.error(error);
        });
    },

    sendChatMessage() {
      if (!this.chat.msgInput) {
        return;
      }
      const chatMsg = this.chat.msgInput;
      this.chat.msgInput = "";

      const msgData = {
        message: chatMsg,
      };

      // this.chat.messages.push(msgData);
      this.sendSignal("chat_message", msgData);
    },

    showChatMsg(msgObj) {
      const { peerUsername, message } = msgObj;
      let dt = Math.ceil(msgObj.dt * 1000);

      this.chat.messages.push({
        dt: dt,
        author: peerUsername,
        message: message,
      });
    },

    sendSignal(msgType, message) {
      this.websocket.send(
        JSON.stringify({
          msgType: msgType,
          message: {
            ...message,
            peerUsername: this.username,
          },
        })
      );
    },

    toggleLocalTrack(value, track) {
      switch (track) {
        case "video":
          this.localStream.tracks.video[0].enabled = value;
          break;
        case "audio":
          this.localStream.tracks.audio[0].enabled = value;
          break;
        default:
          console.log(value, track);
      }
    },

    addLocalTracks(peer) {
      let localStream = this.localStream.mediaStream;
      localStream.getTracks().forEach((track) => {
        peer.addTrack(track, localStream);
      });
    },

    createWebsocket() {
      const location = window.location;
      let wsStart = "ws://";

      if (location.protocol == "https:") {
        wsStart = "wss://";
      }

      // const endPoint = wsStart + location.host + location.pathname
      const endPoint =
        wsStart +
        "localhost:8000/ws" +
        location.pathname +
        `?username=${this.username}`;

      this.websocket = new WebSocket(endPoint);

      // Add websocket event listeners

      // Open
      this.websocket.addEventListener("open", (e) => {
        // console.log(`connection opened, ${JSON.stringify(e)}`);
        this.sendSignal("new_peer", {});
      });

      // Message
      this.websocket.addEventListener("message", (e) => {
        let parsedData = JSON.parse(e.data);
        let peerUsername = parsedData.message.peerUsername;
        let msgType = parsedData["msgType"];
        let receiverChannelName = null;

        if (msgType === "chat_message") {
          // console.log(parsedData);
          this.showChatMsg(parsedData.message);
        } else {
          if (this.username === peerUsername) {
            return;
          }

          switch (msgType) {
            case "new_peer":
              receiverChannelName = parsedData.message.receiver_channel_name;
              this.createOfferer(peerUsername, receiverChannelName);
              return;
            case "new_offer":
              receiverChannelName = parsedData.message.receiver_channel_name;
              let offer = parsedData.message.sdp;
              this.createAnswerer(offer, peerUsername, receiverChannelName);
              return;
            case "new_answer":
              let answer = parsedData.message.sdp;
              let peer = this.getPeer(peerUsername).peer;
              peer.setRemoteDescription(answer);
              return;
            default:
              console.error("UNKNOWN msgType", msgType);
          }
        }
      });

      // Close
      this.websocket.addEventListener("close", (e) => {
        console.log("websocket connection closed");
      });

      // Error
      this.websocket.addEventListener("error", (e) => {
        console.error("websocket error");
      });
    },

    createOfferer(peerUsername, receiverChannelName) {
      // const peer = new RTCPeerConnection(null);
      const peer = new RTCPeerConnection(this.config);

      const remoteStream = new MediaStream();

      peer.addEventListener("track", async (event) => {
        remoteStream.addTrack(event.track, remoteStream);
      });

      this.addLocalTracks(peer);

      const peerDataChannel = peer.createDataChannel("channel");
      this.addPeer(peerUsername, peer, peerDataChannel, remoteStream);

      peer
        .createOffer()
        .then((offer) => peer.setLocalDescription(offer))
        .then(() => {});

      peerDataChannel.addEventListener("open", () => {
        // console.log("connection open RTC");
      });

      peerDataChannel.addEventListener("message", (e) => {
        // console.log(`OFFERER ${JSON.stringify(e.data)}`);
        this.chat.messages.push(JSON.parse(e.data));
      });

      peer.addEventListener("iceconnectionstatechange", () => {
        // if connection state change(disconnect)
        var iceConnectionState = peer.iceConnectionState;

        if (
          iceConnectionState === "failed" ||
          iceConnectionState === "disconnected" ||
          iceConnectionState === "closed"
        ) {
          this.removePeer(peerUsername);

          if (iceConnectionState !== "closed") {
            peer.close();
          }
        }
      });

      peer.addEventListener("icecandidate", (e) => {
        if (e.candidate) {
          // console.log(
          // "new ice candidate",
          // JSON.stringify(peer.localDescription)
          // );
          return;
        }

        this.sendSignal("new_offer", {
          sdp: peer.localDescription,
          receiver_channel_name: receiverChannelName,
        });
      });
    },

    createAnswerer(offer, peerUsername, receiverChannelName) {
      // const peer = new RTCPeerConnection(null);
      const peer = new RTCPeerConnection(this.config);

      const remoteStream = new MediaStream();

      peer.addEventListener("track", async (event) => {
        remoteStream.addTrack(event.track, remoteStream);
      });

      this.addLocalTracks(peer);

      peer
        .setRemoteDescription(offer)
        .then(() => {
          return peer.createAnswer();
        })
        .then((a) => {
          peer.setLocalDescription(a);
        });

      peer.addEventListener("datachannel", (e) => {
        const peerDataChannel = e.channel;
        this.addPeer(peerUsername, peer, peerDataChannel, remoteStream);

        peerDataChannel.addEventListener("open", () => {
          // console.log("connection opened!");
        });

        peerDataChannel.addEventListener("message", (e) => {
          // console.log(`ANSWERER ${JSON.stringify(e.data)}`);
          this.chat.messages.push(JSON.parse(e.data));
        });
      });

      peer.addEventListener("iceconnectionstatechange", () => {
        const iceConnectionState = peer.iceConnectionState;

        if (
          iceConnectionState === "failed" ||
          iceConnectionState === "disconnected" ||
          iceConnectionState === "closed"
        ) {
          this.removePeer(peerUsername);

          if (iceConnectionState !== "closed") {
            peer.close();
          }
        }
      });

      peer.addEventListener("icecandidate", (e) => {
        if (e.candidate) {
          // console.log(
          // "new ice candidate",
          // JSON.stringify(peer.localDescription)
          // );
          return;
        }

        this.sendSignal("new_answer", {
          sdp: peer.localDescription,
          receiver_channel_name: receiverChannelName,
        });
      });
    },
  },
};
</script>
