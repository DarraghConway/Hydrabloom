let pubnub;
let appChannel = "dht22-pi-channel";

const setupPubNub = () => {
  pubnub = new PubNub({
    publishKey: "pub-c-5e5be15e-f582-40f2-8c1a-ca9360199f9d",  // Replace with your actual publish key
    subscribeKey: "sub-c-a2447194-c69b-4dbe-a5e8-a4ed24799246",  // Replace with your actual subscribe key
    userId: "Jack-device",  // Replace with your actual user ID
  });

  // Subscribe to the channel
  pubnub.subscribe({
    channels: [appChannel],
  });

  // Listen for messages
  pubnub.addListener({
    status: (s) => {
      console.log("Status:", s.category);
    },
    message: (messageEvent) => {
      handleMessage(messageEvent.message);  // Handle the incoming message
    },
  });
};

function handleMessage(message) {
  // Check if both temperature and humidity keys exist in the message
  if (message.temperature && message.humidity) {
    document.getElementById("temperature_id").innerHTML = `${message.temperature.toFixed(1)}°C`;
    document.getElementById("humidity_id").innerHTML = `${message.humidity.toFixed(1)}%`;
  }
}
