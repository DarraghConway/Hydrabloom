document.addEventListener("DOMContentLoaded", function () {
  const ledOnButton = document.getElementById("ledOnButton");
  const ledOffButton = document.getElementById("ledOffButton");
  const statusElement = document.getElementById("status");

  let pubnub;
  const sensorsChannel = "sensors-pi-channel";
  const ledChannel = "led-pi-channel";

  // Unified PubNub setup function
  const setupPubNub = () => {
    pubnub = new PubNub({
      publishKey: "pub-c-5e5be15e-f582-40f2-8c1a-ca9360199f9d",
      subscribeKey: "sub-c-a2447194-c69b-4dbe-a5e8-a4ed24799246",
      uuid: "Hydrabloom",
    });

    // Subscribe to both channels
    pubnub.subscribe({
      channels: [sensorsChannel, ledChannel],
    });

    // Set up listeners for both channels
    pubnub.addListener({
      message: handlePubNubMessage,
      status: (statusEvent) => {
        console.log("PubNub status:", statusEvent);
      },
    });
  };

  // General message handler
  const handlePubNubMessage = (event) => {
    const channel = event.channel;
    const message = event.message;

    if (channel === sensorsChannel) {
      handleSensorMessage(message);
    } else if (channel === ledChannel) {
      handleLEDMessage(message);
    } else {
      console.warn("Received message from unknown channel:", channel);
    }
  };

  // Handle messages for the sensors channel
  const handleSensorMessage = (message) => {
    console.log("Received sensor data:", message);

    if (message.temperature !== undefined && message.humidity !== undefined) {
      document.getElementById(
        "temperature_id"
      ).textContent = `${message.temperature.toFixed(1)}°C`;
      document.getElementById(
        "humidity_id"
      ).textContent = `${message.humidity.toFixed(1)}%`;

      storeDHT22Data(message.temperature, message.humidity);
    }

    if (message.lux !== undefined) {
      document.getElementById("lux_id").textContent = `${message.lux.toFixed(
        1
      )} lux`;
      storeTSL2561Data(message.lux);
    }

    // Handle soil moisture data
    if (message.soil_moisture !== undefined) {
      document.getElementById(
        "soil_moisture_id"
      ).textContent = `${message.soil_moisture.toFixed(1)}%`;
      storeSoilMoistureData(message.soil_moisture);
    }
  };

  // Handle messages for the LED channel
  const handleLEDMessage = (message) => {
    console.log("Received LED command:", message);

    if (message.command === "LED_ON") {
      updateStatus("LED is ON");
    } else if (message.command === "LED_OFF") {
      updateStatus("LED is OFF");
    } else {
      console.warn("Unknown LED command:", message.command);
    }
  };

  // Publish LED commands
  const handleClick = (action) => {
    const message = { command: action === "on" ? "LED_ON" : "LED_OFF" };
    publishMessage(ledChannel, message);
  };

  const publishMessage = (channel, message) => {
    pubnub
      .publish({
        channel: channel,
        message: message,
      })
      .then((response) => console.log("Message published:", response))
      .catch((error) => console.error("Error publishing message:", error));
  };

  const updateStatus = (status) => {
    statusElement.textContent = `Status: ${status}`;
  };

  const storeDHT22Data = (temperature, humidity) => {
    fetch("/api/store_dht22_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ temperature, humidity }),
    })
      .then((response) => response.json())
      .then((data) => console.log("DHT22 data stored:", data))
      .catch((error) => console.error("Error storing DHT22 data:", error));
  };

  const storeTSL2561Data = (lux) => {
    fetch("/api/store_tsl2561_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lux }),
    })
      .then((response) => response.json())
      .then((data) => console.log("TSL2561 data stored:", data))
      .catch((error) => console.error("Error storing TSL2561 data:", error));
  };

  const storeSoilMoistureData = (soilMoisture) => {
    fetch("/api/store_soil_moisture_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ soilMoisture }), // Ensure this matches the key expected by the backend
    })
      .then((response) => response.json())
      .then((data) => console.log("Soil moisture data stored:", data))
      .catch((error) =>
        console.error("Error storing soil moisture data:", error)
      );
  };

  // Initialize PubNub
  setupPubNub();

  // Add event listeners for LED control buttons
  ledOnButton.addEventListener("click", () => handleClick("on"));
  ledOffButton.addEventListener("click", () => handleClick("off"));
});
