let pubnub;
let appChannel = "sensors-pi-channel";

const setupPubNub = () => {
  pubnub = new PubNub({
    publishKey: "pub-c-5e5be15e-f582-40f2-8c1a-ca9360199f9d",
    subscribeKey: "sub-c-a2447194-c69b-4dbe-a5e8-a4ed24799246",
    userId: "Jack-device",
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
      handleMessage(messageEvent.message); // Handle the incoming message
    },
  });
};

function handleMessage(message) {
  // Check if temperature and humidity keys exist in the message
  if (message.temperature !== undefined && message.humidity !== undefined) {
    // Update the frontend UI
    document.getElementById(
      "temperature_id"
    ).innerHTML = `${message.temperature.toFixed(1)}°C`;
    document.getElementById(
      "humidity_id"
    ).innerHTML = `${message.humidity.toFixed(1)}%`;

    // Send data to the backend API to store DHT22 data
    storeDHT22Data(message.temperature, message.humidity);
  }

  // Check if lux value is available in the message
  if (message.lux !== undefined) {
    document.getElementById("lux_id").innerHTML = `${message.lux.toFixed(
      1
    )} lux`;

    // Send data to the backend API to store TSL2561 data
    storeTSL2561Data(message.lux);
  }
}

function storeDHT22Data(temperature, humidity) {
  fetch("/api/store_dht22_data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      temperature: temperature,
      humidity: humidity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("DHT22 data stored:", data);
    })
    .catch((error) => {
      console.error("Error storing DHT22 data:", error);
    });
}

function storeTSL2561Data(lux) {
  fetch("/api/store_tsl2561_data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      lux: lux,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("TSL2561 data stored:", data);
    })
    .catch((error) => {
      console.error("Error storing TSL2561 data:", error);
    });
}
