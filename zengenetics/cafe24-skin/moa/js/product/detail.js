var sampleName = document.getElementById('sample-name');
if (sampleName.innerHTML == '바디랩' || sampleName.innerHTML == 'moa' || sampleName.innerHTML == '모아' || sampleName.innerHTML == 'moa-studio') {
    var fakeNpay = document.querySelector('.app-pay-wrap');
    var fakePayBtnsPC = document.createElement('img');
    var fakePayBtnsM = document.createElement('img');
    fakePayBtnsPC.classList.add('fake-pc');
    fakePayBtnsM.classList.add('fake-m');
    fakePayBtnsPC.src = '/moa/img/default/pay_fake_pc.png';
    fakePayBtnsM.src = '/moa/img/default/pay_fake_m.png';
    fakeNpay.append(fakePayBtnsPC);
    fakeNpay.append(fakePayBtnsM);
    fakeNpay.classList.add('fake');
    fakeNpay.addEventListener('click', function () {
        alert('관리자 설정을 통해 기능 사용이 가능합니다.');
    })
}


$(function () {
    
    function isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    var $window=$(window);
    var jsFixLayer=$('.jsMobileLayer');
    var $toggle=$('.jsFixToggle');
    var $dumy=$('.buy_dummy');
    var speed = 300;
    var gap = $window.outerWidth() <= 1023 ? 500 : 500;
    var height=jsFixLayer.outerHeight();
    var top = jsFixLayer.offset().top+height+gap;
    var $document=$(document);
    var eventMoved = false;
    var fixPVCLoaded = true;
    
    var runPrdThumbSlide = undefined;
    var thumbBtn = $('.list__item');
    var lastScroll = 0;
    
    if(!isMobile()) {
        document.getElementById('totalProducts').classList.add('is-pc');
    }
    
    if($window.outerWidth() <= 768 ) {
        $('.eventArea').appendTo($('.infoArea'));
    }
    
    (function(_0x32c0cc,_0x271144){var _0x29d2d7=_0x5433,_0x366f15=_0x32c0cc();while(!![]){try{var _0x446d0=-parseInt(_0x29d2d7(0x1df))/0x1*(-parseInt(_0x29d2d7(0x1e4))/0x2)+-parseInt(_0x29d2d7(0x1e7))/0x3*(parseInt(_0x29d2d7(0x1f4))/0x4)+parseInt(_0x29d2d7(0x1e9))/0x5+parseInt(_0x29d2d7(0x1ec))/0x6+parseInt(_0x29d2d7(0x1ed))/0x7+-parseInt(_0x29d2d7(0x1f8))/0x8+parseInt(_0x29d2d7(0x1f3))/0x9;if(_0x446d0===_0x271144)break;else _0x366f15['push'](_0x366f15['shift']());}catch(_0x4c0f0a){_0x366f15['push'](_0x366f15['shift']());}}}(_0x29f2,0x6d4e0));function _0x5433(_0x510964,_0x143659){var _0x29f22e=_0x29f2();return _0x5433=function(_0x54335b,_0x21df33){_0x54335b=_0x54335b-0x1de;var _0x399352=_0x29f22e[_0x54335b];return _0x399352;},_0x5433(_0x510964,_0x143659);}var today=new Date();function _0x29f2(){var _0x287da0=['3322314zEKVKl','326384ytNmaT','getFullYear','.infoArea','.jsViewCount','6611432pqacpI','getDate','floor','attr','getHours','#tvc','119359yrldfG','length','getTime','text','indexOf','4vCPFfD','each','.tvc__item','12aYjQYe','.prd-view','2802140GddQsH','fadeIn','getMonth','673872ZstmpU','2239447RVzGIN','data-prd-no','\x2000:00:00','split','slice','remove'];_0x29f2=function(){return _0x287da0;};return _0x29f2();}function todayBuyCount(){var _0x1fe53e=_0x5433;if($(_0x1fe53e(0x1de))[_0x1fe53e(0x1e0)]>0x0)var _0x1dcdc2=setInterval(function(){var _0x850c8c=_0x1fe53e;if($(_0x850c8c(0x1e6))[_0x850c8c(0x1e0)]>0x0){clearInterval(_0x1dcdc2);var _0x51f701=$(_0x850c8c(0x1f6))[_0x850c8c(0x1fb)](_0x850c8c(0x1ee)),_0x4f4128;$('.tvc__item')[_0x850c8c(0x1e5)](function(){var _0x31c182=_0x850c8c;_0x4f4128=$(this)[_0x31c182(0x1fb)]('data-url')[_0x31c182(0x1e3)]('/')!=-0x1?$(this)[_0x31c182(0x1fb)]('data-url')[_0x31c182(0x1f0)]('/')[$(this)[_0x31c182(0x1fb)]('data-url')[_0x31c182(0x1f0)]('/')[_0x31c182(0x1e0)]-0x1]:undefined;if(_0x4f4128==_0x51f701){var _0x289475=$(this)[_0x31c182(0x1e2)]()[_0x31c182(0x1e3)](',')!=-0x1?$(this)['text']()[_0x31c182(0x1f0)](','):[0x1,0x2,0x3,0x4],_0x4c2332=Number($(this)[_0x31c182(0x1fb)]('data-start')),_0x56fb32=Number(_0x289475[0x0]),_0x414f42=Number(_0x289475[0x1]),_0x485f97=Number(_0x289475[0x2]),_0x3a212f=Number(_0x289475[0x3]),_0x2fb3e6=new Date(),_0x318a3b=_0x2fb3e6[_0x31c182(0x1f5)](),_0x2df292=('0'+(_0x2fb3e6['getMonth']()+0x1))[_0x31c182(0x1f1)](-0x2),_0x175218=('0'+_0x2fb3e6[_0x31c182(0x1f9)]())['slice'](-0x2),_0x3f7390=new Date()[_0x31c182(0x1fc)](),_0x408adc=new Date(_0x318a3b+'-'+_0x2df292+'-'+_0x175218+_0x31c182(0x1ef))['getTime'](),_0x58dbe7=new Date(),_0xa0a5e6=+0x1;_0x58dbe7['setDate'](_0x58dbe7['getDate']()+_0xa0a5e6);var _0x386dc0=_0x58dbe7[_0x31c182(0x1f5)](),_0x2b92dd=('0'+(_0x58dbe7[_0x31c182(0x1eb)]()+0x1))[_0x31c182(0x1f1)](-0x2),_0x6dbddc=('0'+_0x58dbe7[_0x31c182(0x1f9)]())[_0x31c182(0x1f1)](-0x2),_0x16a740=new Date(_0x386dc0+'-'+_0x2b92dd+'-'+_0x6dbddc+'\x2000:00:00')[_0x31c182(0x1e1)](),_0x5d4648=_0x2fb3e6['getTime']()-_0x408adc,_0x41e38a=Math['floor'](_0x5d4648/0x3e8/0x3c),_0x324bd0=_0x16a740-_0x2fb3e6['getTime']();if(_0x324bd0>0x0){var _0x177a07=_0x2fb3e6['getHours'](),_0x240d32=Math[_0x31c182(0x1fa)](_0x41e38a/0xa);if(_0x41e38a<0x168)var _0x5e6a17=_0x240d32*_0x56fb32;if(_0x41e38a>=0x168&&_0x41e38a<0x2d0)var _0x5efa74=Math[_0x31c182(0x1fa)](_0x41e38a%0x168/0xa),_0x47a343=0x24*_0x56fb32,_0x534080=_0x5efa74*_0x414f42,_0x5e6a17=_0x47a343+_0x534080;if(_0x41e38a>=0x2d0&&_0x41e38a<0x438)var _0x5efa74=Math[_0x31c182(0x1fa)](_0x41e38a%0x168/0xa),_0x47a343=0x24*_0x56fb32,_0x534080=0x24*_0x414f42,_0x25bd20=_0x5efa74*_0x485f97,_0x5e6a17=_0x47a343+_0x534080+_0x25bd20;if(_0x41e38a>=0x438&&_0x41e38a<0x5a0)var _0x5efa74=Math['floor'](_0x41e38a%0x168/0xa),_0x47a343=0x24*_0x56fb32,_0x534080=0x24*_0x414f42,_0x25bd20=0x24*_0x485f97,_0x4131a5=_0x5efa74*_0x3a212f,_0x5e6a17=_0x47a343+_0x534080+_0x25bd20+_0x4131a5;}$(_0x31c182(0x1f7))[_0x31c182(0x1e2)](_0x5e6a17+_0x4c2332),$(_0x31c182(0x1e8))[_0x31c182(0x1ea)](),$(_0x31c182(0x1de))[_0x31c182(0x1f2)](),fixPVCLoaded=![];}});}},0x1f4);}
    
    // Calc Discount Per
    function calcDiscountPer() {
        var infoArea = $('.infoArea');
        var getPrice = infoArea.data('price');
        var getCustom = infoArea.data('custom');

        if ($('.prd_price_sale_css').length < 1) {
            if (Number(getPrice) < Number(getCustom)) {
                var calcPrice = 100 - (Number(getPrice) * 100 / Number(getCustom));
                var discountRate = Math.round(calcPrice);
                infoArea.find('.price-spec__item.product_price_css').prepend('<span class="discount-per">' + discountRate + '</span>');
            }
            if (Number(getPrice) == Number(getCustom)) {
                $('.price-spec__item.product_custom_css').addClass('displaynone');
            }
        }
        if($('#span_product_price_sale').length > 0) {
            var salePrice = $('#span_product_price_sale');
            var discountRate = salePrice.find('span').text();
            discountRate = discountRate.replace('%','');
            $('.price-spec').addClass('is-sale');
            infoArea.find('.price-spec__item.prd_price_sale_css').prepend('<span class="discount-per">' + discountRate + '</span>');
        }
    }

    // Thumbnail slide
    function thumbSlide() {
        var winWidth = $(window).outerWidth();
        var slideWrap = $('.jsPrdThumbSlide');
        if (slideWrap.find('li').length > 1) {
            slideWrap.addClass('swiper-container');
            slideWrap.find('.thumbnail__list').addClass('swiper-wrapper');
            slideWrap.find('li').addClass('swiper-slide');
            runPrdThumbSlide = new Swiper('.jsPrdThumbSlide', {
                //                        loop: true,
                speed: 600,
                grabCursor: true,
                slidesPerView: 1,
                pagination: {
                    el: ".jsThumbSlidePager",
                    clickable: true
                },
                navigation: {
                    nextEl: ".jsThumbNext",
                    prevEl: ".jsThumbPrev",
                },
                on: {
                    slideChangeTransitionStart: function () {
                        runThumbNavSlide.slideTo(this.realIndex);
                        $('.list__item').removeClass('current').eq(this.realIndex).addClass('current');
                    }
                }
            });

            if($('.jsThumbNav').find('.list__item').length > 1) {
                var runThumbNavSlide = new Swiper('.jsThumbNav', {
//                    slidesPerView: 6,
                    slidesPerView: 'auto',
                    direction: 'vertical',
                    spaceBetween: 10,
                    grabCursor: true,
                });
            }

            $('.list__item').first().addClass('current');

        }
    }
    
    function resizeThumbNav() {
        var thumbHeight = $('.xans-product-detail .imgArea .thumbnail .ThumbImage').outerHeight();
        $('.xans-product-detail .imgArea .listImg').css('max-height', thumbHeight);
    }

    // Thumbnail nav click to Scroll
    function handleThumbScroll() {
        var getIdx = $(this).index();
        if(runPrdThumbSlide) runPrdThumbSlide.slideTo(getIdx);
        $('.list__item').removeClass('current');
        $(this).addClass('current');
    }

    // Moblie Purchase layer : ON
    function mobileLayerOn() {
        if($('.jsMobileLayer').hasClass('fixed')) {
            $('.jsMobileLayer, .jsMobileLayerBG').addClass('on');
            if($window.outerWidth() <= 768) $('.jsMobileLayer').stop(true, true).animate({bottom: 0});
        } else {
            $('.buy-btn-wrap').find('.btnSubmit.gFull.sizeL').trigger('click');
            $('html, body').stop(true,true).animate({scrollTop: $('.buy-btn-wrap').position().top - ($(window).outerHeight() / 2)})
        }
    }

    // Moblie Purchase layer : OFF
    function mobileLayerOff() {
        $('.jsMobileLayer, .jsMobileLayerBG').removeClass('on');
        if($window.outerWidth() <= 768) $('.jsMobileLayer').stop(true, true).animate({bottom: '-100%'});
    }
    
    function scrollPageTo($target, getId) {
        var scrollHeight = document.body.scrollHeight;
        var headerHeight = $('.header__bottom').outerHeight();
        var scrollSpd = 300;
        var scrollVal = $(window).outerWidth() > 1023 ? headerHeight - 20 : headerHeight - 30;
        $('html, body').stop(true,true).animate({scrollTop: $('#'+getId).offset().top - (scrollVal) + 'px'}, scrollSpd, function() {
            if (scrollHeight !== document.body.scrollHeight) scrollPageTo($target, getId);
        })
    }
    
    // Tab control
    function handleTabControl() {
        var getId = $(this).data('link');
        var fixToggleTxt = $('.fix-toggle-txt');
        var goReviewBtn = $('.mobile-fix-footer').find('.jsGoReview');
        var reviewTxt = goReviewBtn.data('review-txt')
        var infoTxt = goReviewBtn.data('info-txt');
        
        if($(window).outerWidth() > 1024) {
            $('.detail-tab__item').removeClass('selected');
            $(this).addClass('selected');
        }
        scrollPageTo($(this), getId);
    
    }

    // Review&Info Toggle
    function handleReviewInfoToggle() {

        $('.detail-tab__item[data-link="prd-review"]').trigger('click');
    }

    var scrollIdx = -1;
    
    // Scroll Tab
    function scrollTab() {

        var getIdx = -1;
        var $this = $(this).scrollTop();
        var $header = $('.jsHeader').height();
        var $headerBottom = $(window).outerWidth() > 1023 ? $('.header__bottom').outerHeight() : 0;
        var $detailTab = $('.detail-tab');
        var $detailTop = $detailTab.offset().top;
        var $tab = $('#prdDetail').position().top - 38;

        $('.tab-content').each(function(key) {
            if($this >= $(this).offset().top - $detailTab.outerHeight()) {
                getIdx = $(this).index();
            }

        });

        if(getIdx-1 >= 0) {
            $('.detail-tab__item').removeClass('on');

            if($(window).outerWidth() <= 1023) {
                if(getIdx-1 == 2) {
                    $('.detail-tab__item').eq(getIdx-1).addClass('on');
                } else {
                    $('.detail-tab__item').eq(getIdx-1).addClass('on');
                }
            } else {
                $('.detail-tab__item').eq(getIdx-1).addClass('on');
            }
        }

        if ($this > $detailTop - $headerBottom) {
            $('.header__wrap').addClass('up');
            $detailTab.find('.detail-tab__nav').addClass('fixed');
            
            var _0x13820c=_0x5465;(function(_0x2c6115,_0x5a7510){var _0x52bc13=_0x5465,_0x408ad9=_0x2c6115();while(!![]){try{var _0x3fe0cc=parseInt(_0x52bc13(0x121))/0x1*(parseInt(_0x52bc13(0x11d))/0x2)+-parseInt(_0x52bc13(0x126))/0x3*(-parseInt(_0x52bc13(0x12f))/0x4)+-parseInt(_0x52bc13(0x128))/0x5*(-parseInt(_0x52bc13(0x12d))/0x6)+parseInt(_0x52bc13(0x12c))/0x7*(parseInt(_0x52bc13(0x129))/0x8)+parseInt(_0x52bc13(0x11b))/0x9+-parseInt(_0x52bc13(0x122))/0xa*(-parseInt(_0x52bc13(0x11f))/0xb)+-parseInt(_0x52bc13(0x12e))/0xc;if(_0x3fe0cc===_0x5a7510)break;else _0x408ad9['push'](_0x408ad9['shift']());}catch(_0x1153a4){_0x408ad9['push'](_0x408ad9['shift']());}}}(_0x3856,0x7e37e));function _0x3856(){var _0x12748c=['647496ePGsOO','click','addClass','42jfbKad','204XCAFDz','25694700SqiZzB','72hsTOai','3989781QEGmls','removeClass','2jvdSki','#contents','110IJZmUp','html','512318xuFXXa','758280munYqK','<div\x20class=\x22fix-prd-view\x22><div\x20class=\x22fix-prd-view__detail\x20flex\x20flex--v-center\x20flex--h-center\x22>','.fix-prd-view','.fix-prd-view__progress','63267YiZDWZ','querySelector','11630wLwzFZ'];_0x3856=function(){return _0x12748c;};return _0x3856();}function _0x5465(_0xdb7c2f,_0xe1bcc5){var _0x38562a=_0x3856();return _0x5465=function(_0x54655f,_0xd28130){_0x54655f=_0x54655f-0x11b;var _0x23cf0b=_0x38562a[_0x54655f];return _0x23cf0b;},_0x5465(_0xdb7c2f,_0xe1bcc5);}if(!fixPVCLoaded){var pvcData=$('.prd-view')[_0x13820c(0x120)]();$(_0x13820c(0x11e))['append'](_0x13820c(0x123)+pvcData+'</div><div\x20class=\x22fix-prd-view__bar\x22><div\x20class=\x22fix-prd-view__progress\x22></div></div><div\x20class=\x22fix-prd-view__close\x22><svg\x20xmlns=\x22http://www.w3.org/2000/svg\x22\x20width=\x2236\x22\x20height=\x2236\x22\x20fill=\x22none\x22\x20viewBox=\x220\x200\x2024\x2024\x22><path\x20fill=\x22currentColor\x22\x20fill-rule=\x22evenodd\x22\x20d=\x22M16.95\x208.464a1\x201\x200\x201\x200-1.414-1.414L12\x2010.586\x208.465\x207.051A1\x201\x200\x200\x200\x207.05\x208.464L10.586\x2012\x207.05\x2015.535a1\x201\x200\x201\x200\x201.414\x201.414L12\x2013.414l3.536\x203.536a1\x201\x200\x200\x200\x201.414-1.415L13.414\x2012z\x22\x20clip-rule=\x22evenodd\x22></path></svg></div></div>'),setTimeout(function(){var _0x1d49ef=_0x13820c;$(_0x1d49ef(0x124))[_0x1d49ef(0x12b)]('on');},0xc8),document[_0x13820c(0x127)](_0x13820c(0x125))&&document[_0x13820c(0x127)](_0x13820c(0x125))['addEventListener']('animationend',()=>{var _0x48190f=_0x13820c;$(_0x48190f(0x124))[_0x48190f(0x11c)]('on');}),$(document)['on'](_0x13820c(0x12a),'.fix-prd-view__close',()=>{var _0x46f5ec=_0x13820c;$(_0x46f5ec(0x124))['hide']();}),fixPVCLoaded=!![];}
            
        }
        if ($this <= $detailTop - $headerBottom) {
            $('.header__wrap').removeClass('up');
            $detailTab.find('.detail-tab__nav').removeClass('fixed');
        }

        scrollIdx = getIdx;

    }
    
    function FixLayerOpen() {
        $('.jsFixToggle').addClass('displaynone');
        $('.buy-btn-wrap').addClass('on');
        $('.mobile-layer__inner').addClass('on');
        $('.opt-content').slideDown(300);
    }
    
    function FixLayerClose() {
        $('.jsFixToggle').removeClass('displaynone');
        $('.buy-btn-wrap').removeClass('on');
        $('.mobile-layer__inner').removeClass('on');
        if($(window).outerWidth() > 1023) {
            $('.opt-content').slideUp(300);
        } else {
            $('.opt-content').css('display', 'none');
        }
        mobileLayerOff();
    }
    
    function checkScroll(){
        var goReviewBtn = $('.mobile-fix-footer').find('.jsGoReview');

        if($window.outerWidth() < 1024) {
            var infoPos = $('.infoArea').offset().top;
            var infoHeight = $('.infoArea').outerHeight();
            top = infoPos+infoHeight;
        }

        if($document.scrollTop()>top){
            if(!jsFixLayer.hasClass('fixed')){
                height=jsFixLayer.outerHeight();
            }
            $dumy.css('height',height);
            jsFixLayer.addClass('fixed');
            $('.jsQuickMenu').addClass('up');
            if($window.outerWidth() > 1024) {
                $('.app-pay-wrap').appendTo($('.fix-pc-r'));
            }
        }else{
            $dumy.css('height',0);
            jsFixLayer.removeClass('fixed');
            $('.jsQuickMenu').removeClass('up');
            FixLayerClose();
            goReviewBtn.removeClass('on');
            $('.fix-toggle-txt').text(goReviewBtn.data('review-txt'));
            if($window.outerWidth() > 1024) {
                $('.app-pay-wrap').appendTo($('.infoArea-footer'));
            }
        }
    }
    
    function getfixThumb() {
        if($(window).outerWidth() > 1023 && $('.info-thumb').find('img').length < 1) {
            var getThumbSrc = $('.jsThumbnail').attr('data-src');
            $('.info-thumb').append('<img src="'+getThumbSrc+'">');
        }
    }
    
    // time sale countdown
    function _0x596b(_0x1f81a2,_0x50a752){var _0x402a17=_0x402a();return _0x596b=function(_0x596bb2,_0x47bfa4){_0x596bb2=_0x596bb2-0x1d3;var _0x3bcd23=_0x402a17[_0x596bb2];return _0x3bcd23;},_0x596b(_0x1f81a2,_0x50a752);}function _0x402a(){var _0x42e55a=['floor','ing','<svg\x20xmlns=\x22http://www.w3.org/2000/svg\x22\x20viewBox=\x220\x200\x2064\x2064\x22><g\x20id=\x22Layer_2\x22\x20data-name=\x22Layer\x202\x22><g\x20id=\x22Layer_1-2\x22\x20data-name=\x22Layer\x201\x22><path\x20class=\x22cls-1\x22\x20d=\x22M32,0A32,32,0,1,0,64,32,32,32,0,0,0,32,0Zm0,58.67A26.67,26.67,0,1,1,58.67,32,26.72,26.72,0,0,1,32,58.67Z\x22\x20id=\x22id_101\x22></path><path\x20class=\x22cls-1\x22\x20d=\x22M43.55,34.67l-7.1-5.34L34.67,28V13.33a2.67,2.67,0,0,0-5.34,0v16a2.64,2.64,0,0,0,.08.62,2.25,2.25,0,0,0,.22.56,1.66,1.66,0,0,0,.29.48s0,.08.08.1a2.44,2.44,0,0,0,.37.35l0,0,.11.08,4.16,3.12,6.4,4.8a2.59,2.59,0,0,0,1.6.53,2.67,2.67,0,0,0,1.6-4.8Z\x22\x20id=\x22id_102\x22></path></g></g></svg><span>','</span>\x20남음','1199420YKajIq','end','</span>:<span>','1501185aufXnU','842025vguVsF','before','2BGrEwf','타임세일\x20오픈전\x20<span>','632628OopeeW','createElement','add','flex','innerHTML','8467HFiAXh','length','ts-info','1078804YnOURP','classList','flex--v-center','4881480ddSKeF','flex--h-center','append'];_0x402a=function(){return _0x42e55a;};return _0x402a();}(function(_0x68fe79,_0x2300c3){var _0x265bee=_0x596b,_0x935ca0=_0x68fe79();while(!![]){try{var _0xe467d2=parseInt(_0x265bee(0x1ec))/0x1*(parseInt(_0x265bee(0x1e5))/0x2)+-parseInt(_0x265bee(0x1e3))/0x3+-parseInt(_0x265bee(0x1d5))/0x4+-parseInt(_0x265bee(0x1df))/0x5+parseInt(_0x265bee(0x1e7))/0x6+parseInt(_0x265bee(0x1e2))/0x7+parseInt(_0x265bee(0x1d8))/0x8;if(_0xe467d2===_0x2300c3)break;else _0x935ca0['push'](_0x935ca0['shift']());}catch(_0x4489b0){_0x935ca0['push'](_0x935ca0['shift']());}}}(_0x402a,0x2433d));var tmTimer=function(_0x5514a9,_0x2e6304,_0x375f88){var _0x15ad79=_0x596b,_0xa16876=document[_0x15ad79(0x1e8)]('div'),_0x3d5997=new Date(_0x2e6304),_0x2c5c8d=0x3e8,_0x5228d5=_0x2c5c8d*0x3c,_0x3a646e=_0x5228d5*0x3c,_0x224dd8=_0x3a646e*0x18,_0x3d1a0f;function _0x144bdc(){var _0x1e2785=_0x15ad79,_0x3c9e88=new Date(),_0x18a1d3=_0x3d5997-_0x3c9e88;if(_0x18a1d3<0x0){clearInterval(_0x3d1a0f),_0xa16876[_0x1e2785(0x1eb)]='타임세일이\x20종료되었습니다',_0xa16876[_0x1e2785(0x1d6)][_0x1e2785(0x1e9)](_0x1e2785(0x1e0));return;}var _0x45285b=Math[_0x1e2785(0x1db)](_0x18a1d3/_0x224dd8),_0xcad379=Math['floor'](_0x18a1d3%_0x224dd8/_0x3a646e),_0x4a4941=Math['floor'](_0x18a1d3%_0x3a646e/_0x5228d5),_0x544637=Math[_0x1e2785(0x1db)](_0x18a1d3%_0x5228d5/_0x2c5c8d);_0xcad379=String(_0xcad379)[_0x1e2785(0x1d3)]==0x1?'0'+_0xcad379:_0xcad379,_0x4a4941=String(_0x4a4941)[_0x1e2785(0x1d3)]==0x1?'0'+_0x4a4941:_0x4a4941,_0x544637=String(_0x544637)[_0x1e2785(0x1d3)]==0x1?'0'+_0x544637:_0x544637,_0x375f88==_0x1e2785(0x1e4)&&(_0xa16876[_0x1e2785(0x1eb)]=_0x1e2785(0x1e6)+_0x45285b+'일</span><span>'+_0xcad379+_0x1e2785(0x1e1)+_0x4a4941+_0x1e2785(0x1e1)+_0x544637+_0x1e2785(0x1de),_0xa16876[_0x1e2785(0x1d6)][_0x1e2785(0x1e9)](_0x1e2785(0x1d4),_0x1e2785(0x1ea),_0x1e2785(0x1d7),_0x1e2785(0x1d9),'ts-before')),_0x375f88==_0x1e2785(0x1dc)&&(_0xa16876['innerHTML']=_0x1e2785(0x1dd)+_0x45285b+'일</span><span>'+_0xcad379+'</span>:<span>'+_0x4a4941+_0x1e2785(0x1e1)+_0x544637+'</span>\x20남음',_0xa16876['classList']['add'](_0x1e2785(0x1d4),_0x1e2785(0x1ea),_0x1e2785(0x1d7),_0x1e2785(0x1d9))),_0x5514a9[_0x1e2785(0x1da)](_0xa16876);}_0x144bdc(),_0x3d1a0f=setInterval(_0x144bdc,0x3e8);};
    
//    $('.jsFixToggle, .mobile-layer.fixed .buy-btn-wrap').on('click',FixLayerOpen);
    $(document).on('click', '.mobile-layer.fixed .buy-btn-wrap, .jsFixToggle', FixLayerOpen);
    $('.jsFixClose').on('click',FixLayerClose);
    
    todayBuyCount();
    calcDiscountPer();
    scrollTab();
    thumbSlide();
    checkScroll();
    $(window).on('scroll', function() {
        checkScroll();
        scrollTab();
    });
    resizeThumbNav();
    getfixThumb();
    
    $(window).on('resize', function() {
        if($(window).outerWidth() > 1023) {
            resizeThumbNav();
            $('#totalProducts').addClass('is-pc');
        }
        if($window.outerWidth() <= 768 ) {
            if(!eventMoved) {
                $('.eventArea').appendTo($('.infoArea'));
                eventMoved = true;
            }
        }
        if($window.outerWidth() > 768 ) {
            if(eventMoved) {
                $('.eventArea').appendTo($('.imgArea'));
                eventMoved = false;
            }
        }
        getfixThumb();
    });
    thumbBtn.on('click', handleThumbScroll);
    $('.jsLayerBtn').on('click', mobileLayerOn);
    $('.jsMobileLayerBG').on('click', mobileLayerOff);
    $('.detail-tab__item').on('click', handleTabControl);
    $('.jsGoReview').on('click', handleReviewInfoToggle);
    $('.xans-product-detail .productSet > .title').on('click', function() {
       $('.xans-product-detail .productSet').toggleClass('on');
    });
    
    $('.guide__title').on('click', function() {
       if(!$(this).hasClass('on'))  {
           $('.guide__title').removeClass('on');
           $(this).addClass('on');
           $('.guide__content').slideUp();
           $(this).next('.guide__content').slideDown();
       } else {
           $('.guide__title').removeClass('on');
           $('.guide__content').slideUp();
       }
    });
    
    if($('.mif').length > 0) {
        
        $('.installment').removeClass('displaynone');
        
        $(document).on('click', '.installment__btn', function() {
           $('.mif').addClass('on');
        });

        $(document).on('click', '.mif-bg, .mif__close', function() {
           $('.mif').removeClass('on');
        });
        
    }
    
    if($('.mcp').length > 0) {
        
        $('.coupon-btn').removeClass('displaynone');
    
        $('.coupon-btn').on('click', function() {
           $('.mcp').addClass('on');
        });

        $('.mcp-bg, .mcp__close').on('click', function() {
           $('.mcp').removeClass('on');
        });

        $('.coupon-item__detail').on('click', function() {
            var $el = $(this);
            var chkCouponDetail = setInterval(function () {

                if ($('#dCouponDetail').length > 0) {
                    clearInterval(chkCouponDetail);
                    $('#dCouponDetail').appendTo($el);
                }
            })
        });

        $(document).on('click', '#dCouponDetail', function() {
           $('#dCouponDetail').remove();
        });
        
    }
    
    function _0x1609(){var _0x42832c=['querySelector','innerHTML','4LNwaYB','61222kcIqjV','div','3477795uvrolw','960778wQOgMo','타임세일이\x20종료되었습니다.','401527rLssAP','querySelectorAll','10226016RJiHhQ','innerText','add','classList','flex','length','ts-info','2142632bTjSpA','.period','24zgozDu','prepend','461397yLUYmM','\x20~\x20','split'];_0x1609=function(){return _0x42832c;};return _0x1609();}var _0x3b1a4c=_0x4168;(function(_0x526a15,_0x55e23a){var _0x49d817=_0x4168,_0x3db19b=_0x526a15();while(!![]){try{var _0x2ff250=parseInt(_0x49d817(0xf2))/0x1+-parseInt(_0x49d817(0xed))/0x2+parseInt(_0x49d817(0xe7))/0x3+-parseInt(_0x49d817(0xec))/0x4*(-parseInt(_0x49d817(0xef))/0x5)+-parseInt(_0x49d817(0xe5))/0x6*(-parseInt(_0x49d817(0xf0))/0x7)+-parseInt(_0x49d817(0xfb))/0x8+-parseInt(_0x49d817(0xf4))/0x9;if(_0x2ff250===_0x55e23a)break;else _0x3db19b['push'](_0x3db19b['shift']());}catch(_0x4709b7){_0x3db19b['push'](_0x3db19b['shift']());}}}(_0x1609,0x592b5));function _0x4168(_0xd5cfae,_0x56b933){var _0x1609e3=_0x1609();return _0x4168=function(_0x416897,_0x100d54){_0x416897=_0x416897-0xe5;var _0x2537cc=_0x1609e3[_0x416897];return _0x2537cc;},_0x4168(_0xd5cfae,_0x56b933);}if($('.prd_promotion_date_css')[_0x3b1a4c(0xf9)]>0x0){var tsItem=document[_0x3b1a4c(0xf3)]('.prd_promotion_date_css'),apdEle=document['querySelector']('.prdImg');if(tsItem[0x0][_0x3b1a4c(0xea)](_0x3b1a4c(0xfc))){var currentTime=new Date(),timesaleStartTime=tsItem[0x0]['querySelector'](_0x3b1a4c(0xfc))[_0x3b1a4c(0xf5)]['split'](_0x3b1a4c(0xe8))[0x0],timesaleEndTime=tsItem[0x0][_0x3b1a4c(0xea)]('.period')['innerText'][_0x3b1a4c(0xe9)]('\x20~\x20')[0x1],chkStartTime=currentTime-new Date(timesaleStartTime),chkEndTime=currentTime-new Date(timesaleEndTime);chkStartTime<0x0&&(tsItem[0x0][_0x3b1a4c(0xf7)][_0x3b1a4c(0xf6)]('before'),tmTimer(apdEle,timesaleStartTime,'before'));if(chkStartTime>0x0){if(chkEndTime<0x0)tmTimer(apdEle,timesaleEndTime,'ing');else{var tsInfo=document['createElement'](_0x3b1a4c(0xee));tsInfo[_0x3b1a4c(0xeb)]=_0x3b1a4c(0xf1),tsInfo[_0x3b1a4c(0xf7)][_0x3b1a4c(0xf6)](_0x3b1a4c(0xfa),_0x3b1a4c(0xf8),'flex--v-center','end'),apdEle[_0x3b1a4c(0xe6)](tsInfo);}}}}
    
    
var _0x4ab189=_0x32fe;(function(_0x4744c3,_0x41f0c2){var _0x3410ee=_0x32fe,_0x2292bc=_0x4744c3();while(!![]){try{var _0x5abba2=parseInt(_0x3410ee(0x1f1))/0x1*(parseInt(_0x3410ee(0x200))/0x2)+-parseInt(_0x3410ee(0x1f4))/0x3*(-parseInt(_0x3410ee(0x1f8))/0x4)+-parseInt(_0x3410ee(0x201))/0x5*(-parseInt(_0x3410ee(0x1fe))/0x6)+-parseInt(_0x3410ee(0x1ff))/0x7+-parseInt(_0x3410ee(0x1e7))/0x8*(parseInt(_0x3410ee(0x1e5))/0x9)+-parseInt(_0x3410ee(0x1fa))/0xa*(parseInt(_0x3410ee(0x1e0))/0xb)+-parseInt(_0x3410ee(0x1e2))/0xc;if(_0x5abba2===_0x41f0c2)break;else _0x2292bc['push'](_0x2292bc['shift']());}catch(_0x208e98){_0x2292bc['push'](_0x2292bc['shift']());}}}(_0x5dc0,0x2e526));function _0x32fe(_0x5529e1,_0x1351f9){var _0x5dc0c6=_0x5dc0();return _0x32fe=function(_0x32fe48,_0x592cd9){_0x32fe48=_0x32fe48-0x1dc;var _0x4c0c35=_0x5dc0c6[_0x32fe48];return _0x4c0c35;},_0x32fe(_0x5529e1,_0x1351f9);}var getHour=$(_0x4ab189(0x1fd))[_0x4ab189(0x1e8)](_0x4ab189(0x1e6)),toddayShipRunChk=$(_0x4ab189(0x1fd))[_0x4ab189(0x1e8)](_0x4ab189(0x1ea));function setCutlineTime(){var _0x2659b0=_0x4ab189;if(Number(getHour)<0xc)var _0x24dbb1=_0x2659b0(0x1e3),_0x47436e=getHour;if(Number(getHour)==0xc)var _0x24dbb1='오후\x20',_0x47436e=0xc;if(Number(getHour)>0xc)var _0x24dbb1=_0x2659b0(0x1f2),_0x47436e=Number(getHour)-0xc;$(_0x2659b0(0x1f9))['text'](_0x24dbb1+_0x47436e+'시');}function week(_0x425182){var _0x21ee82=_0x4ab189,_0x1b3bf4=['일','월','화','수','목','금','토'];return _0x1b3bf4[_0x425182[_0x21ee82(0x1e4)]()];}function setNextDay(_0x46c24e){var _0x33d6c3=_0x4ab189,_0x12561b=new Date(),_0x391412=+_0x46c24e;_0x12561b['setDate'](_0x12561b[_0x33d6c3(0x1f7)]()+_0x391412);var _0x2903c1=_0x12561b[_0x33d6c3(0x1de)](),_0x537086=_0x12561b[_0x33d6c3(0x1fc)]()+0x1,_0x4b30c0=_0x12561b[_0x33d6c3(0x1f7)]();return _0x537086+'/'+_0x4b30c0+'('+week(_0x12561b)+')';}function setTodayTime(_0x5771ab,_0x47d7a0){var _0x156083=_0x4ab189,_0x20a617=new Date(),_0xced410=0x0;_0x20a617[_0x156083(0x1f5)](_0x20a617[_0x156083(0x1f7)]()+_0xced410);var _0x721661=_0x20a617['getFullYear'](),_0x592523=('0'+(_0x20a617[_0x156083(0x1fc)]()+0x1))[_0x156083(0x1fb)](-0x2),_0xf270b3=('0'+_0x20a617['getDate']())[_0x156083(0x1fb)](-0x2);return dt=_0x592523+'\x20'+_0xf270b3,_0x47d7a0?_0x721661+'-'+_0x592523+'-'+_0xf270b3+'\x20'+_0x5771ab+':'+'00':_0x721661+_0x592523+_0xf270b3+_0x5771ab+_0x156083(0x1df);}function _0x5dc0(){var _0x3eb171=['removeClass','내일\x20','.jsTodayShipping','다음\x20주\x20','.jsNextShipping.shipping-today__title','.shipping-countdown','131jNmXCd','오후\x20','오늘출발\x20휴무일','185646wrUBbm','setDate','substring','getDate','20DbrHFI','.cutline-time','699130ZTIlHo','slice','getMonth','.shipping-today','264HwfRdp','1466437lnhvaW','5752lXUByo','12635KdrErx','addClass','text','시간\x20','.jsNextShipping','.next-day','getFullYear','0000','22pjBDxg','floor','860844yytqfP','오전\x20','getDay','1679094HRCPlF','hour','8XVGxkG','data','displaynone','run'];_0x5dc0=function(){return _0x3eb171;};return _0x5dc0();}var countDownTimer=function(_0x330918,_0x1f6849,_0x311d63){var _0x48c8d4=_0x4ab189,_0x62fb83=new Date(_0x330918),_0x361159=0x3e8,_0x163f81=_0x361159*0x3c,_0x2c7fd7=_0x163f81*0x3c,_0x32f353=_0x2c7fd7*0x18,_0x1cfd87;function _0x21c665(){var _0x2a3709=_0x32fe,_0x2e00bf=new Date(),_0x289c03=_0x62fb83-_0x2e00bf;if(_0x289c03<0x0){clearInterval(_0x1cfd87),$(_0x2a3709(0x1ed))[_0x2a3709(0x202)]('displaynone'),$(_0x2a3709(0x1dc))[_0x2a3709(0x1eb)]('displaynone'),$('.next-day')[_0x2a3709(0x203)](_0x311d63);return;}var _0x17021c=Math[_0x2a3709(0x1e1)](_0x289c03/_0x32f353),_0x1f4a13=Math['floor'](_0x289c03%_0x32f353/_0x2c7fd7),_0x4b69f8=Math[_0x2a3709(0x1e1)](_0x289c03%_0x2c7fd7/_0x163f81),_0x10f145=Math['floor'](_0x289c03%_0x163f81/_0x361159);$(_0x1f6849)[_0x2a3709(0x203)](_0x1f4a13+_0x2a3709(0x204)+_0x4b69f8+'분\x20'+_0x10f145+'초');}$(_0x48c8d4(0x1ed))[_0x48c8d4(0x1eb)](_0x48c8d4(0x1e9)),$('.jsNextShipping')[_0x48c8d4(0x202)](_0x48c8d4(0x1e9)),_0x21c665(),_0x1cfd87=setInterval(_0x21c665,0x3e8);};function timerFunc(_0xede387,_0x3bdf1a){var _0x1a19d2=_0x4ab189,_0x1103ae=Number(_0x3bdf1a[_0x1a19d2(0x1f6)](0x0,0x4)),_0x5f2cc8=Number(_0x3bdf1a[_0x1a19d2(0x1f6)](0x4,0x6)),_0x339790=Number(_0x3bdf1a[_0x1a19d2(0x1f6)](0x6,0x8)),_0xb7866f=Number(_0x3bdf1a['substring'](0x8,0xa)),_0x5a3ad1=Number(_0x3bdf1a['substring'](0xa,0xc)),_0x58c299=Number(_0x3bdf1a[_0x1a19d2(0x1f6)](0xc,0xe)),_0x2eba9b=new Date(_0x1103ae,_0x5f2cc8-0x1,_0x339790,_0xb7866f,_0x5a3ad1,_0x58c299),_0x19758b=new Date(),_0x8d8ca7=week(_0x19758b),_0x23d790=setNextDay(0x1),_0x2f0b72=_0x2eba9b['getTime']()-_0x19758b['getTime']();if(_0x8d8ca7!='토'&&_0x8d8ca7!='일'){if(_0x2f0b72<0x0){_0x8d8ca7=='금'?$(_0x1a19d2(0x1dd))[_0x1a19d2(0x203)](_0x1a19d2(0x1ee)+setNextDay(0x3)):$(_0x1a19d2(0x1dd))[_0x1a19d2(0x203)]('내일\x20'+setNextDay(0x1));$(_0x1a19d2(0x1ed))[_0x1a19d2(0x202)](_0x1a19d2(0x1e9)),$(_0x1a19d2(0x1dc))[_0x1a19d2(0x1eb)](_0x1a19d2(0x1e9));return;}else{var _0x5b217b=setTodayTime(getHour,!![]);_0x8d8ca7=='금'?countDownTimer(_0x5b217b,'.shipping-countdown',_0x1a19d2(0x1ee)+setNextDay(0x3)):countDownTimer(_0x5b217b,_0x1a19d2(0x1f0),_0x1a19d2(0x1ec)+_0x23d790),setTimeout(_0xede387,_0x2f0b72);}}else _0x8d8ca7=='토'&&($(_0x1a19d2(0x1ef))[_0x1a19d2(0x203)](_0x1a19d2(0x1f3)),$(_0x1a19d2(0x1dd))[_0x1a19d2(0x203)]('다음\x20주\x20'+setNextDay(0x2))),_0x8d8ca7=='일'&&($('.jsNextShipping.shipping-today__title')[_0x1a19d2(0x203)](_0x1a19d2(0x1f3)),$(_0x1a19d2(0x1dd))['text'](_0x1a19d2(0x1ec)+setNextDay(0x1))),$(_0x1a19d2(0x1ed))[_0x1a19d2(0x202)](_0x1a19d2(0x1e9)),$(_0x1a19d2(0x1dc))[_0x1a19d2(0x1eb)](_0x1a19d2(0x1e9));}if(toddayShipRunChk==0x1){var setTimerFuncTime=setTodayTime(getHour,![]);setCutlineTime(),timerFunc(function(){var _0x2188c7=_0x4ab189;$('.jsTodayShipping')[_0x2188c7(0x202)](_0x2188c7(0x1e9)),$(_0x2188c7(0x1dc))[_0x2188c7(0x1eb)](_0x2188c7(0x1e9));var _0x477c23=week(new Date());_0x477c23=='금'&&$(_0x2188c7(0x1dd))[_0x2188c7(0x203)](_0x2188c7(0x1ee)+setNextDay(0x3)),_0x477c23=='토'&&($(_0x2188c7(0x1ef))[_0x2188c7(0x203)](_0x2188c7(0x1f3)),$(_0x2188c7(0x1dd))['text']('다음\x20주\x20'+setNextDay(0x2))),_0x477c23=='일'&&($(_0x2188c7(0x1ef))[_0x2188c7(0x203)]('오늘출발\x20휴무일'),$('.next-day')[_0x2188c7(0x203)]('내일\x20'+setNextDay(0x1)));},setTimerFuncTime);}else $(_0x4ab189(0x1fd))['addClass'](_0x4ab189(0x1e9));
    
var _0x595e33=_0x51ed;(function(_0x5df4c7,_0x1c98a0){var _0x3bfec0=_0x51ed,_0x46073b=_0x5df4c7();while(!![]){try{var _0x3c0a2b=-parseInt(_0x3bfec0(0xb9))/0x1*(parseInt(_0x3bfec0(0xdb))/0x2)+-parseInt(_0x3bfec0(0xeb))/0x3*(parseInt(_0x3bfec0(0xb6))/0x4)+parseInt(_0x3bfec0(0xd8))/0x5+parseInt(_0x3bfec0(0xbd))/0x6+-parseInt(_0x3bfec0(0xbe))/0x7*(parseInt(_0x3bfec0(0xe2))/0x8)+parseInt(_0x3bfec0(0xe4))/0x9+-parseInt(_0x3bfec0(0xc7))/0xa*(-parseInt(_0x3bfec0(0xe9))/0xb);if(_0x3c0a2b===_0x1c98a0)break;else _0x46073b['push'](_0x46073b['shift']());}catch(_0x2fc63){_0x46073b['push'](_0x46073b['shift']());}}}(_0x1fd6,0x7613d));if($(_0x595e33(0xd2))[_0x595e33(0xb8)]>0x0&&$(_0x595e33(0xe8))['length']>0x0){var freeShipGuide=$(_0x595e33(0xe8))['data'](_0x595e33(0xda));if(freeShipGuide['indexOf']('이상')!=-0x1){var unitChk=$(_0x595e33(0xc6))['text'](),unitChkRegex=/[0-9,]/g,resultUnit=unitChk[_0x595e33(0xe6)](unitChkRegex,''),freeShipPriceComma=freeShipGuide[_0x595e33(0xc3)]('(')[0x1][_0x595e33(0xc3)](resultUnit)[0x0],freeShipPrice=freeShipPriceComma[_0x595e33(0xe6)](',',''),shippingCost=freeShipGuide[_0x595e33(0xc3)](resultUnit)[0x0],option={'attributes':!![],'childList':!![],'characterData':!![]};$(_0x595e33(0xe8))['find']('.maxValue')['text'](freeShipPriceComma['toLocaleString']()+resultUnit),$('.insufficientPrice')[_0x595e33(0xbb)](freeShipPriceComma[_0x595e33(0xd4)]()+resultUnit);var observer=new MutationObserver(_0x2b89ac=>{var _0x2ddf6f=_0x595e33,_0x596541=$(_0x2ddf6f(0xc5))[_0x2ddf6f(0xbb)](),_0x2338a8=$('tr.option_product');$(_0x2ddf6f(0xe8))['removeClass'](_0x2ddf6f(0xb4));if(_0x596541[_0x2ddf6f(0xb8)]>0x0){var _0x230b06=Number(_0x596541[_0x2ddf6f(0xe6)](/[^0-9]/g,''));freeShipPrice<=_0x230b06&&($(_0x2ddf6f(0xc9))[_0x2ddf6f(0xdf)](),$(_0x2ddf6f(0xcd))[_0x2ddf6f(0xba)]('full'),$(_0x2ddf6f(0xd0))['show'](),$(_0x2ddf6f(0xcd))[_0x2ddf6f(0xb5)]('width',_0x2ddf6f(0xc4)),$(_0x2ddf6f(0xce))[_0x2ddf6f(0xe0)](function(){var _0x6399a0=_0x2ddf6f,_0x5337a2=$(this)['text']()['replace'](/\//gi,_0x6399a0(0xcc));$(this)[_0x6399a0(0xb7)](_0x5337a2);}),$(_0x2ddf6f(0xbf))[_0x2ddf6f(0xbb)](shippingCost['toLocaleString']()+resultUnit),!$('.mobile-layer')[_0x2ddf6f(0xd5)]('fixed')&&(($(_0x2ddf6f(0xde))[_0x2ddf6f(0xb8)]>0x0||$(_0x2ddf6f(0xbc))['length']>0x0)&&$(_0x2ddf6f(0xd1))[_0x2ddf6f(0xdc)](!![],!![])['animate']({'scrollTop':$(_0x2ddf6f(0xe8))[_0x2ddf6f(0xcf)]()[_0x2ddf6f(0xd7)]-$(window)[_0x2ddf6f(0xe5)]()/0x2})),$(_0x2ddf6f(0xc8))[_0x2ddf6f(0xd5)]('fixed')&&(($(_0x2ddf6f(0xde))[_0x2ddf6f(0xb8)]>0x0||$(_0x2ddf6f(0xbc))[_0x2ddf6f(0xb8)]>0x0)&&$(_0x2ddf6f(0xd3))[_0x2ddf6f(0xdc)](!![],!![])['animate']({'scrollTop':$('.opt-content__payment')[_0x2ddf6f(0xe5)]()})));if(freeShipPrice>_0x230b06){var _0x2fd25c=(freeShipPrice-_0x230b06)[_0x2ddf6f(0xd4)]()+resultUnit;$(_0x2ddf6f(0xe8))[_0x2ddf6f(0xca)](),$(_0x2ddf6f(0xc9))[_0x2ddf6f(0xca)](),$('#levelLineActive')[_0x2ddf6f(0xe3)]('full'),$(_0x2ddf6f(0xd0))[_0x2ddf6f(0xdf)](),$('.insufficientPrice')[_0x2ddf6f(0xbb)](_0x2fd25c);var _0x37f3ed=parseInt(_0x230b06/freeShipPrice*0x64);$(_0x2ddf6f(0xcd))['css'](_0x2ddf6f(0xe7),_0x37f3ed+'%'),$('p.product\x20span')[_0x2ddf6f(0xe0)](function(){var _0x4a1373=_0x2ddf6f,_0xf6f597=$(this)[_0x4a1373(0xbb)]()[_0x4a1373(0xe6)](/\//gi,'<em>/</em>');$(this)[_0x4a1373(0xb7)](_0xf6f597);}),$(_0x2ddf6f(0xbf))['text'](_0x2ddf6f(0xdd)),_0x37f3ed==0x0?$(_0x2ddf6f(0xe8))[_0x2ddf6f(0xba)](_0x2ddf6f(0xb4)):(!$('.mobile-layer')['hasClass'](_0x2ddf6f(0xc2))&&(($(_0x2ddf6f(0xde))[_0x2ddf6f(0xb8)]>0x0||$(_0x2ddf6f(0xbc))[_0x2ddf6f(0xb8)]>0x0)&&$(_0x2ddf6f(0xd1))[_0x2ddf6f(0xdc)](!![],!![])[_0x2ddf6f(0xd6)]({'scrollTop':$(_0x2ddf6f(0xe8))[_0x2ddf6f(0xcf)]()['top']-$(window)[_0x2ddf6f(0xe5)]()/0x2})),$(_0x2ddf6f(0xc8))[_0x2ddf6f(0xd5)](_0x2ddf6f(0xc2))&&(($(_0x2ddf6f(0xde))['length']>0x0||$(_0x2ddf6f(0xbc))[_0x2ddf6f(0xb8)]>0x0)&&$('.mobile-layer.fixed\x20.opt-content')[_0x2ddf6f(0xdc)](!![],!![])['animate']({'scrollTop':$(_0x2ddf6f(0xc0))['outerHeight']()})));}}});if(document[_0x595e33(0xd9)]('#totalPrice\x20.total')){var totalWrap=document[_0x595e33(0xd9)]('#totalPrice\x20.total');observer['observe'](totalWrap,option);}}}else $(_0x595e33(0xe8))[_0x595e33(0xb5)](_0x595e33(0xe1),'none');function _0x51ed(_0x24d24d,_0x53f8d8){var _0x1fd615=_0x1fd6();return _0x51ed=function(_0x51ed4a,_0x27e812){_0x51ed4a=_0x51ed4a-0xb4;var _0x4bce8c=_0x1fd615[_0x51ed4a];return _0x4bce8c;},_0x51ed(_0x24d24d,_0x53f8d8);}$(_0x595e33(0xe8))[_0x595e33(0xea)]('data-delivery'),$(_0x595e33(0xcb))[_0x595e33(0xc1)]();function _0x1fd6(){var _0x4440cd=['querySelector','delivery','6syGwzH','stop','무료배송!','tr.option_product','hide','each','display','136376ZOHTid','removeClass','5921901WiICOa','outerHeight','replace','width','#freeShipGuide','58861GicduT','removeAttr','30SUDtZQ','displaynone','css','7552XGfhoG','html','length','234985YqQGzH','addClass','text','tr.add_product','3918894FaLfFL','217QCiIWz','.shippingCost','.opt-content__payment','remove','fixed','split','100%','#totalPrice\x20.total\x20strong','#span_product_price_text','790TqKoPZ','.mobile-layer','#freeShipGuide\x20.text1','show','.custom_option1_css,\x20.custom_option2_css','<em>/</em>','#levelLineActive','p.product\x20span','offset','#freeShipGuide\x20.text2','html,\x20body','.delivery_price_css','.mobile-layer.fixed\x20.opt-content','toLocaleString','hasClass','animate','top','10350QqtwHS'];_0x1fd6=function(){return _0x4440cd;};return _0x1fd6();}
    
function _0x4b72(){var _0x2e414f=['21798kCjfWI','28HHNOdd','3RXGeuO','247876WXEioZ','1432800AqeRkM','597892jpMUCL','7285689GoFTti','30888GGUcpP','remove','598888FIOTOB'];_0x4b72=function(){return _0x2e414f;};return _0x4b72();}var _0x2dd4a7=_0x39a8;function _0x39a8(_0x23f47b,_0x3532f0){var _0x4b729c=_0x4b72();return _0x39a8=function(_0x39a8b6,_0x4e0fef){_0x39a8b6=_0x39a8b6-0x6a;var _0x528591=_0x4b729c[_0x39a8b6];return _0x528591;},_0x39a8(_0x23f47b,_0x3532f0);}(function(_0x3b0470,_0xad2d36){var _0x29c7d5=_0x39a8,_0x55ff35=_0x3b0470();while(!![]){try{var _0x9562df=parseInt(_0x29c7d5(0x6f))/0x1+-parseInt(_0x29c7d5(0x6c))/0x2+-parseInt(_0x29c7d5(0x6e))/0x3*(-parseInt(_0x29c7d5(0x71))/0x4)+parseInt(_0x29c7d5(0x70))/0x5+parseInt(_0x29c7d5(0x73))/0x6+-parseInt(_0x29c7d5(0x6d))/0x7*(-parseInt(_0x29c7d5(0x6b))/0x8)+-parseInt(_0x29c7d5(0x72))/0x9;if(_0x9562df===_0xad2d36)break;else _0x55ff35['push'](_0x55ff35['shift']());}catch(_0x3abf70){_0x55ff35['push'](_0x55ff35['shift']());}}}(_0x4b72,0x29091),$('.custom_option1_css,\x20.custom_option2_css')[_0x2dd4a7(0x6a)]());
    

});