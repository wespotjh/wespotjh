$(document).ready(function(){
    var prdSlide = new Swiper('.indexPrdSwiper', {
        speed: 500,
        //grabCursor: true,
        slidesPerView: 4,
        //spaceBetween: 24,
        navigation: {
            nextEl: ".indexPrdNext",
            prevEl: ".indexPrdPrev",
        },
        pagination: {
            el: ".indexPrdPager",
            type: 'fraction',
            //clickable: true,
        },
        breakpoints: {
/*             1280: {
                slidesPerView: 4,
            },
            1023: {
                slidesPerView: 3,
            }, */
            767: {
                //freeMode: true,
                slidesPerView: 1,
                spaceBetween: 10,
            }
        }

    }); 
});