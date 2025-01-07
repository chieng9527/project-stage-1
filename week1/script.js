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