// 點擊漢堡按鈕，顯示選單
document.querySelector('.hamburger-icon').addEventListener('click', function () {
  const menu = document.querySelector('.menu');
  menu.classList.add('open');
});

// 點擊關閉按鈕，隱藏選單
document.querySelector('.close-btn').addEventListener('click', function () {
  const menu = document.querySelector('.menu');
  menu.classList.remove('open');
});

// Assignment-1 資料來源
const assignment1Url = "https://padax.github.io/taipei-day-trip-resources/taipei-attractions-assignment-1";

// 分割 filelist 字串為圖片網址陣列的函數
function extractImageUrls(filelist) {
  const regex = /(https.*?\.jpg)/gi;
  return filelist.match(regex) || [];
}

// 定義全局變量
let attractions = [];
let bigBoxIndex = 3;
const renderBatchSize = 10;

// 獲取資料並初始化
fetch(assignment1Url)
  .then(response => response.json())
  .then(data => {
    attractions = data.data.results;

    renderSmallBoxes();
    renderBigBoxes();

    // 綁定按鈕點擊事件
    const loadMoreButton = document.querySelector('button');
    loadMoreButton.addEventListener('click', renderBigBoxes);
  });

// 渲染小盒子
function renderSmallBoxes() {
  const smallBoxesContainer = document.querySelector('.small-boxes');
  attractions.slice(0, 3).forEach(attraction => {
    if (!attraction.stitle || !attraction.filelist) return;

    const smallBox = document.createElement('div');
    smallBox.classList.add('small-box');

    const imageUrls = extractImageUrls(attraction.filelist);
    const imgUrl = imageUrls[0] || "./default-image.png";

    const img = document.createElement('img');
    img.src = imgUrl;
    img.alt = attraction.stitle;

    const p = document.createElement('p');
    p.textContent = attraction.stitle;

    smallBox.appendChild(img);
    smallBox.appendChild(p);
    smallBoxesContainer.appendChild(smallBox);
  });
}

// 渲染大盒子
function renderBigBoxes() {
  const bigBoxesContainer = document.querySelector('.big-boxes');
  const loadMoreButton = document.querySelector('button');

  const nextBatch = attractions.slice(bigBoxIndex, bigBoxIndex + renderBatchSize);
  const fragment = document.createDocumentFragment();

  nextBatch.forEach(attraction => {
    if (!attraction.stitle || !attraction.filelist) return;

    const bigBox = document.createElement('div');
    bigBox.classList.add('big-box');

    const imageUrls = extractImageUrls(attraction.filelist);
    const imgUrl = imageUrls[0] || "./default-image.png";
    bigBox.style.backgroundImage = `url('${imgUrl}')`;

    const textBlock = document.createElement('div');
    textBlock.classList.add('text-block');
    textBlock.textContent = attraction.stitle;

    const starIcon = document.createElement('img');
    starIcon.src = "./star-icon.png";
    starIcon.classList.add('star-icon');
    starIcon.alt = "Star";

    bigBox.appendChild(textBlock);
    bigBox.appendChild(starIcon);
    fragment.appendChild(bigBox);
  });

  bigBoxesContainer.appendChild(fragment);
  bigBoxIndex += renderBatchSize;

  if (bigBoxIndex >= attractions.length) {
    loadMoreButton.style.display = 'none';
  }
}