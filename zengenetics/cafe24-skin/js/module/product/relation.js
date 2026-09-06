$(function() {
    
    var initCnt = $(window).width() >= 768 ? 4 : 0;
    
	function _0x252d(){var _0x526fbb=['447160XyScJz','541871CURfaQ','65JTyZwm','4952UMbPsX','201582qeKqzB','</span>','indexOf','1581712uMUpMt','sale','17577414VlAvwD','data','prepend','.price','length','replace','1812aXyxqa','5591936QIfQRr','round'];_0x252d=function(){return _0x526fbb;};return _0x252d();}function _0x593d(_0xf80a52,_0x1fe920){var _0x252de3=_0x252d();return _0x593d=function(_0x593d91,_0xf3fb6b){_0x593d91=_0x593d91-0x127;var _0xc35ca5=_0x252de3[_0x593d91];return _0xc35ca5;},_0x593d(_0xf80a52,_0x1fe920);}(function(_0x141a9d,_0x18f904){var _0x2b6f3d=_0x593d,_0x46cdde=_0x141a9d();while(!![]){try{var _0x118bb3=parseInt(_0x2b6f3d(0x130))/0x1+parseInt(_0x2b6f3d(0x136))/0x2+parseInt(_0x2b6f3d(0x12c))/0x3*(parseInt(_0x2b6f3d(0x132))/0x4)+parseInt(_0x2b6f3d(0x131))/0x5*(-parseInt(_0x2b6f3d(0x133))/0x6)+parseInt(_0x2b6f3d(0x12d))/0x7+parseInt(_0x2b6f3d(0x12f))/0x8+-parseInt(_0x2b6f3d(0x138))/0x9;if(_0x118bb3===_0x18f904)break;else _0x46cdde['push'](_0x46cdde['shift']());}catch(_0xca4912){_0x46cdde['push'](_0x46cdde['shift']());}}}(_0x252d,0x85287),$('.jsRelatedItem')['each'](function(){var _0x840a15=_0x593d,_0x3cc529=$(this)[_0x840a15(0x127)](_0x840a15(0x137)),_0x4cf20e=$(this)[_0x840a15(0x127)]('price');_0x3cc529['indexOf']('원')!=-0x1&&(_0x3cc529=_0x3cc529[_0x840a15(0x12b)]('원',''));_0x4cf20e[_0x840a15(0x135)]('원')!=-0x1&&(_0x4cf20e=_0x4cf20e[_0x840a15(0x12b)]('원',''));if(_0x3cc529[_0x840a15(0x12a)]>0x0){if(_0x3cc529!=_0x4cf20e){var _0x29903d=0x64-_0x3cc529*0x64/_0x4cf20e,_0x270cde=Math[_0x840a15(0x12e)](_0x29903d);$(this)['find'](_0x840a15(0x129))[_0x840a15(0x128)]('<span\x20class=\x22sale-per\x22>'+_0x270cde+_0x840a15(0x134));}}}));
   
    if($('.jsRelatedItem').length > initCnt) {
        
        var relatedSlide = new Swiper('.jsRelatedSlide', {
            loop: true,
            speed: 600,
            grabCursor: true,
            slidesPerView: $('.jsRelatedSlide').data('slide-view'),
            spaceBetween: 20,
            navigation: {
                nextEl: ".jsPrdNext",
                prevEl: ".jsPrdPrev",
            },
            pagination: {
                el: ".related-pager",
                clickable: true
            },
            breakpoints: {
                767: {
                    slidesPerView: 2,
                    slidesPerGroup: 2,
                    loop: false,
                    spaceBetween: 16,
                }
            }
        });
        $('.prd-nav-wrap').addClass('on');
    }
    
});