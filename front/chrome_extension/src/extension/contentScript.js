// contentScript.js

function waitForDetailButton(intervalTime = 500, maxAttempts = 20) {
  return new Promise((resolve) => {
    let attemptCount = 0;
    const intervalId = setInterval(() => {
      attemptCount++;
      const button = Array.from(document.querySelectorAll('button, a, div'))
        .find(el => el.textContent.trim() === '상세정보 펼쳐보기');
      if (button) {
        clearInterval(intervalId);
        button.click();
        resolve(true);
      } else if (attemptCount >= maxAttempts) {
        clearInterval(intervalId);
        resolve(false);
      }
    }, intervalTime);
  });
}

function findIntroduceDiv(root = document) {
  const walker = document.createTreeWalker(
    root,
    NodeFilter.SHOW_ELEMENT,
    {
      acceptNode: (node) => {
        if (node.id === 'INTRODUCE') {
          return NodeFilter.FILTER_ACCEPT;
        }
        return NodeFilter.FILTER_SKIP;
      }
    },
    false
  );

  let node = walker.nextNode();
  if (node) return node;

  const shadowHosts = Array.from(root.querySelectorAll('*')).filter(el => el.shadowRoot);
  for (const host of shadowHosts) {
    const found = findIntroduceDiv(host.shadowRoot);
    if (found) return found;
  }

  return null;
}

function findAllImages(root) {
  let images = Array.from(root.querySelectorAll('img'));
  const shadowRoots = Array.from(root.querySelectorAll('*')).filter(el => el.shadowRoot);
  shadowRoots.forEach(el => {
    images = images.concat(findAllImages(el.shadowRoot));
  });
  return images;
}

function waitForIntroduceDiv(timeout = 10000) {
  return new Promise((resolve) => {
    const introduceDiv = findIntroduceDiv();
    if (introduceDiv) {
      resolve();
      return;
    }

    const observer = new MutationObserver(() => {
      const target = findIntroduceDiv();
      if (target) {
        observer.disconnect();
        resolve();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    setTimeout(() => {
      observer.disconnect();
      console.warn('INTRODUCE div did not appear within the specified time.');
      resolve();
    }, timeout);
  });
}

function getIntroduceData() {
  const introduceDiv = findIntroduceDiv();
  if (!introduceDiv) {
    console.warn('Cannot found [INTRODUCE] div');
    return {
      text: '',
      images: []
    };
  }

  const introduceText = introduceDiv.innerText.trim();
  const imagesInIntroduce = findAllImages(introduceDiv);
  const imageLinks = imagesInIntroduce.map(img => img.src).filter(link => !!link);

  return {
    text: introduceText,
    images: imageLinks
  };
}

function createBlackBanner(thumbnailUrl, productName, productPrice, productDesc) {
  const banner = document.createElement('div');
  banner.id = 'custom-black-banner';
  banner.style.position = 'fixed';
  banner.style.top = '0';
  banner.style.left = '0';
  banner.style.width = '100%';
  banner.style.backgroundColor = '#000';
  banner.style.color = '#fff';
  banner.style.padding = '15px';
  banner.style.display = 'flex';
  banner.style.flexDirection = 'column';
  banner.style.justifyContent = 'center';
  banner.style.alignItems = 'flex-start';
  banner.style.zIndex = '100000';
  banner.style.boxSizing = 'border-box';

  const firstLine = document.createElement('div');
  firstLine.style.display = 'flex';
  firstLine.style.width = '100%';
  firstLine.style.alignItems = 'center';
  firstLine.style.marginBottom = '8px';

  const thumbnail = document.createElement('img');
  thumbnail.src = thumbnailUrl || '';
  thumbnail.alt = '제품 썸네일';
  thumbnail.style.width = '60px';
  thumbnail.style.height = '60px';
  thumbnail.style.objectFit = 'cover';
  thumbnail.style.marginRight = '10px';

  const nameSpan = document.createElement('span');
  nameSpan.textContent = productName || '제품명 없음';
  nameSpan.style.fontSize = '16px';
  nameSpan.style.fontWeight = 'bold';
  nameSpan.style.marginRight = '10px';

  const priceSpan = document.createElement('span');
  priceSpan.textContent = productPrice || '가격 정보 없음';
  priceSpan.style.fontSize = '16px';
  priceSpan.style.color = '#FFEE58';
  priceSpan.style.fontWeight = 'bold';

  firstLine.appendChild(thumbnail);
  firstLine.appendChild(nameSpan);
  firstLine.appendChild(priceSpan);

  const secondLine = document.createElement('div');
  secondLine.id = 'custom-black-banner-desc';
  secondLine.style.marginTop = '8px';
  secondLine.style.fontSize = '14px';
  secondLine.style.lineHeight = '1.4';
  secondLine.textContent = productDesc || '제품 설명 없음';

  const closeBtn = document.createElement('button');
  closeBtn.textContent = 'X';
  closeBtn.style.position = 'absolute';
  closeBtn.style.right = '10px';
  closeBtn.style.top = '10px';
  closeBtn.style.background = 'none';
  closeBtn.style.color = '#fff';
  closeBtn.style.border = 'none';
  closeBtn.style.cursor = 'pointer';
  closeBtn.style.fontSize = '16px';

  closeBtn.addEventListener('click', () => {
    banner.remove();
    document.body.style.paddingTop = '0';
  });

  banner.appendChild(firstLine);
  banner.appendChild(secondLine);
  banner.appendChild(closeBtn);

  document.body.appendChild(banner);
  document.body.style.paddingTop = `${banner.offsetHeight}px`;
}

function watchForIntroduceTag(callback) {
  if (findIntroduceDiv()) {
    callback();
    return;
  }

  const observer = new MutationObserver((mutations, obs) => {
    if (findIntroduceDiv()) {
      obs.disconnect();
      callback();
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });

  setTimeout(() => {
    observer.disconnect();
    console.warn('INTRODUCE div did not appear within the specified time.');
  }, 10000);
}

/** 
 * 수집된 데이터를 저장해둘 전역 변수 
 * (팝업에서 요청 시 응답하기 위해)
 */
let collectedData = {
  text: '',
  images: []
};

async function main() {
  const buttonClicked = await waitForDetailButton();
  if (buttonClicked) {
    console.log('"상세정보 펼쳐보기" button clicked');
  } else {
    console.warn('"상세정보 펼쳐보기" button not found');
  }

  await waitForIntroduceDiv();

  const { text, images } = getIntroduceData();
  collectedData.text = text;
  collectedData.images = images;

  chrome.runtime.sendMessage({
    type: 'PRODUCT_DATA_TO_SEND',
    payload: { text, images }
  });

  // name
  let productName = '제품명 없음';
  const nameElem = document.querySelector('h3._22kNQuEXmb'); 
  if (nameElem) {
    productName = nameElem.textContent.trim();
  }

  // price
  let productPrice = '가격 정보 없음';
  const priceElem = document.querySelector('strong.aICRqgP9zw._2oBq11Xp7s span._1LY7DqCnwR');
  if (priceElem) {
    productPrice = `${priceElem.textContent.trim()}원`;
  }

  // thumbnail
  let productThumbnail = '';
  const thumbElem = document.querySelector('._2tT_gkmAOr > img._2RYeHZAP_4');
  if (thumbElem) {
    productThumbnail = thumbElem.getAttribute('src') || '';
  }

  createBlackBanner(productThumbnail, productName, productPrice, text);

  chrome.runtime.sendMessage({
    type: 'PRODUCT_INTRODUCE_DATA',
    payload: {
      name: window.location.href,
      images: images
    }
  }, function(response) {
    if (chrome.runtime.lastError) {
      console.error('background error:', chrome.runtime.lastError);
      return;
    }

    console.log('background response:', response);
    
    const newDescription = Array.isArray(response?.data?.texts)
      ? response.data.texts.join('\n')
      : '추가 설명 없음';

    const bannerDesc = document.getElementById('custom-black-banner-desc');
    if (bannerDesc) {
      bannerDesc.textContent = newDescription;
      console.log('banner updated');
    } else {
      console.warn('cannot find banner description element');
    }
  });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request?.type === 'GET_INTRODUCE_DATA') {
    sendResponse(collectedData);
    return true;
  }
});


(function(){
  watchForIntroduceTag(main);
})();