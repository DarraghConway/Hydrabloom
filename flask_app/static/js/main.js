let pubnub;
let appChannel = "dht22-pi-channel";

const setupPubNub = () => {
  pubnub = new PubNub({
    publishKey: "your_publish_key",
    subscribeKey: "your_subscribe_key",
    userId: "your_user_id",
  });

  const channel = pubnub.channel(appChannel);
  const subscription = channel.subscription();

  pubnub.addListener({
    status: (s) => {
      console.log("Status", s.category);
    },
  });

  subscription.onMessage = (messageEvent) => {
    handleMessage(messageEvent.message);
  };

  subscription.subscribe();
};

function handleMessage(message) {
  if ("temperature_c" in message && "humidity" in message) {
    document.getElementById(
      "temperature_id"
    ).innerHTML = `${message.temperature_c.toFixed(1)}°C`;
    document.getElementById(
      "humidity_id"
    ).innerHTML = `${message.humidity.toFixed(1)}%`;
  }
}
