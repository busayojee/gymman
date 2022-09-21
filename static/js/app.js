// Burger menu
let burger = document.querySelector('.burger');
let navlist = document.querySelector('.navlist');
burger.addEventListener('click', slideMenu);
function slideMenu(){
    burger.classList.toggle('switch_menu');
    navlist.classList.toggle('toggle_navigation');
};

var fullbox = document.getElementById("fullbox");
var fullimg = document.getElementById("fullimg");
function openf(pic){
    fullbox.style.display = 'flex';
    fullimg.src = pic;
}
function closef(){
    fullbox.style.display = 'none';
}
// slideshow
// var myIndex = 0;
// carousel();

// function carousel() {
//   var i;
//   var x = document.getElementsByClassName("mySlides");
//   for (i = 0; i < x.length; i++) {
//     x[i].style.display = "none";  
//   }
//   myIndex++;
//   if (myIndex > x.length) {myIndex = 1}    
//   x[myIndex-1].style.display = "block";  
//   setTimeout(carousel, 2000); // Change image every 2 seconds
// }

AOS.init(
    {
        delay:50,
    }
);