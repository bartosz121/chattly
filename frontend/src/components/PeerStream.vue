<template>
  <video
    class="h-full"
    :srcObject="this.peerObj.remoteStream"
    :id="this.peerObj.peerName"
    autoplay
    playsinline
  ></video>
</template>

<script>
export default {
  name: "PeerStream",
  props: {
    peerObj: Object,
  },
};
</script>