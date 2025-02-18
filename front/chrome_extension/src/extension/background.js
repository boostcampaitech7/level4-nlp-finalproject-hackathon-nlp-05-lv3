// background.js

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const BASE_URL = "http://localhost:8080/" // TODO: 서버 URL 변수화

  if (message.type === 'PRODUCT_INTRODUCE_DATA') {
    const { name, images } = message.payload;

    const data = {
      link: name,
      images: images
    };

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: JSON.stringify(data),
      redirect: "follow"
    };

    const apiUrl = BASE_URL + "api/image-to-text";

    fetch(apiUrl, requestOptions)
      .then(response => response.json())
      .then(result => {
        console.log('API response:', result);
        sendResponse({ success: true, data: result });
      })
      .catch(error => {
        console.error('API error:', error);
        sendResponse({ success: false, error: error.toString() });
      });

    return true;
  }

  if (message.type === "PRODUCT_DATA_TO_SEND") {
    console.log('background received:', message.payload);
  }
});