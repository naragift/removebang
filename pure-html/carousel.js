
const carouselContainer = document.querySelector('.carousel-container');
const cardWidth = carouselContainer.querySelector('.card').offsetWidth;
let currentPosition = 0;

function slide(direction) {
const offset = direction === 'next' ? -cardWidth : cardWidth;
currentPosition += offset;
carouselContainer.style.transform = `translateX(${currentPosition}px)`;
}

