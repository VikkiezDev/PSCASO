// // Initialization for ES Users
// import { Carousel, initMDB } from "mdb-ui-kit";

// initMDB({ Carousel });

// Simple carousel script
const images = document.querySelectorAll('.carousel img');
let currentImage = 0;

function nextImage() {
    images[currentImage].classList.remove('active');
    currentImage = (currentImage + 1) % images.length;
    images[currentImage].classList.add('active');
}

setInterval(nextImage, 5000); // Change image every 5 seconds