var cateIdx;
var skwdLoaded = undefined;
var skwdCloned = false;
var header = $('.jsHeader');
var todayBtn = document.querySelector('.jsTodayBtn');
var closeBtn = document.querySelector('.jsTodayClose');
var todayPopup = document.querySelector('.today-view');
var todayBG = document.querySelector('.jsTodayBG');
var cateSumWidth = 16;
var loadedCateSlide = false;

function loadEft() {
    $('html').addClass('loaded');
}

function setFlowBanner() {
    var runTopBanner = new Swiper('.jsTopBanner', {
        loop: true,
        speed: 700,
        grabCursor: true,
        slidesPerView: 1,
        direction: 'vertical',
        autoplay: {
            delay: 2500,
            disableOnInteraction: false,
        }
    });
}

function chkThisPageCate() {
    var pathTitle = $('.path li').eq(1).text();

    $('.category__item').each(function () {
        if (pathTitle.indexOf($(this).children('.category__link').text()) != -1) {
            cateIdx = $(this).index();
        }
    });

    if (!cateIdx && $('.path').closest('.xans-board').length > 0) {
        cateIdx = $('.category__item--board').index();
    }

    $('.category__item').eq(cateIdx).addClass('current');
}

function cateSlide() {

    if ($(window).outerWidth() < 768 && !loadedCateSlide) {

        $('.category__item').each(function () {
            cateSumWidth += $(this).outerWidth() + Number($(this).css("marginRight").replace('px', ''));
        });

        if (cateSumWidth >= $(window).outerWidth()) {
            var runCateSlide = new Swiper('.jsHCateSlide', {
                slidesPerView: 'auto',
                freeMode: true,
                slideClass: 'category__item'
            });
            runCateSlide.slideTo((cateIdx - 1), 0);
        }
        
        loadedCateSlide = true;

    } else {
        if (runCateSlide && loadedCateSlide) {
            runCateSlide.destroy();
            loadedCateSlide = false;
        }
    }

}

// Scroll header fixed
function scrollHeaderFixed() {
    var getScroll = $(window).scrollTop();
    var loss = $('.header__bottom').position().top + 25;
    var quickMenu = $('.jsQuickMenu');
    var mCutLine = $('.top-banner').length > 0 ? $('.top-banner').outerHeight() : 0;
    if (getScroll >= loss) {
        header.addClass('fixed');
        $('.all-c').addClass('up');
        quickMenu.addClass('on');
    }
    if (getScroll > mCutLine) {
        header.addClass('m-fixed');
        $('#wrap').addClass('m-fixed');
        $('.jsTopBanner').addClass('m-fixed');

    }
    if (getScroll < loss) {
        header.removeClass('fixed')
        $('.all-c').removeClass('up');;
        quickMenu.removeClass('on');

        if ($(window).outerWidth() > 1024) handleSearchOff();
    }
    if (getScroll <= mCutLine) {
        header.removeClass('m-fixed');
        $('#wrap').removeClass('m-fixed');
        $('.jsTopBanner').removeClass('m-fixed');
    }
}

function handleSearchOn() {

    if ($('.jsSearchBtn').hasClass('on')) {
        handleSearchOff();
    } else {
        if ($(window).outerWidth() < 1024) $('html, body').css('overflow', 'hidden');
        $('.jsSearchBtn').addClass('on');
        $('.search').addClass('on');
        handleAllCateClose();
    }

    const _0x217573=_0x154e;function _0x154e(_0x1d7d0e,_0x224f36){const _0x54ab27=_0x54ab();return _0x154e=function(_0x154e18,_0x354d57){_0x154e18=_0x154e18-0x81;let _0x3da91d=_0x54ab27[_0x154e18];return _0x3da91d;},_0x154e(_0x1d7d0e,_0x224f36);}(function(_0x15212f,_0x3668cd){const _0x1677c4=_0x154e,_0x2525f9=_0x15212f();while(!![]){try{const _0x3bc955=parseInt(_0x1677c4(0x87))/0x1+-parseInt(_0x1677c4(0x84))/0x2+parseInt(_0x1677c4(0x8b))/0x3*(parseInt(_0x1677c4(0x8a))/0x4)+-parseInt(_0x1677c4(0x8c))/0x5+-parseInt(_0x1677c4(0x8e))/0x6*(parseInt(_0x1677c4(0x89))/0x7)+parseInt(_0x1677c4(0x86))/0x8*(parseInt(_0x1677c4(0x82))/0x9)+parseInt(_0x1677c4(0x91))/0xa;if(_0x3bc955===_0x3668cd)break;else _0x2525f9['push'](_0x2525f9['shift']());}catch(_0x239c6d){_0x2525f9['push'](_0x2525f9['shift']());}}}(_0x54ab,0x7f8a6));function _0x54ab(){const _0x43db04=['.skwd-recent__empty','parse','9297cPihFZ','displaynone','1742588mqFmbf','removeClass','1192ROgGSL','60207PuFAak','.recent__delete','59647IfMyAU','42384BsfHAl','177UWatyh','2396045ozqJda','forEach','198QeCRJn','length','getItem','13148140WOHoxI'];_0x54ab=function(){return _0x43db04;};return _0x54ab();}if(!skwdLoaded){const savedToDos=JSON[_0x217573(0x81)](localStorage[_0x217573(0x90)](TODOS_KEY));savedToDos!==null&&savedToDos[_0x217573(0x8f)]>0x0&&(toDos=savedToDos,savedToDos[_0x217573(0x8d)](paintToDo),$(_0x217573(0x88))[_0x217573(0x85)]('displaynone')),(!savedToDos||savedToDos[_0x217573(0x8f)]<0x1)&&$(_0x217573(0x92))[_0x217573(0x85)](_0x217573(0x83)),skwdLoaded=!![];}
}

function handleSearchOff() {
    if ($(window).outerWidth() < 1024) $('html, body').css('overflow', 'visible');
    $('.jsSearchBtn').removeClass('on');
    header.removeClass('search-on');
    $('.search').removeClass('on');
}

function pageScrollUp() {
    $('html, body').animate({
        scrollTop: 0
    }, 400);
}

function handleTodayOpen() {
    var popupInner = document.querySelector('.today-view__inner');
    var TVCont = document.createElement("iframe");
    TVCont.setAttribute("id", "today-view");
    TVCont.setAttribute("frameborder", "0");
    TVCont.setAttribute("height", "175px");
    TVCont.style.width = "338px";
    TVCont.src = "/moa/import/popup/today_view_cont.html";
    popupInner.append(TVCont);
    todayPopup.classList.add('on', 'is-animate')
}

function handleTodayClose() {
    $('.today-view').removeClass('on');
    setTimeout(function () {
        $('#today-view').remove();
    }, 400);
}

function handleCartClose() {
    var cartData = $('#cart-data');
    cartData.removeClass('on');
    setTimeout(function () {
        cartData.remove();
        $('#cart-script').remove();
    }, 700);
}

function handleCartOpen(e) {
    $.ajax({
        url: '/moa/import/popup/cart_data.html',
        dataType: 'html',
        success: function (result) {
            $('body').append(result);
            $('#cart-data').addClass('on');
        },
        complete: function () {
            $('.cart-loading').addClass('stop');
            $('.jsCartClose, .cart-data-bg').on('click', handleCartClose);
        }
    });
    e.preventDefault();
}

function handleFooterDropdown() {
    if (!$(this).hasClass('on')) {
        $(this).addClass('on').next('.footer__info').slideDown();
    } else {
        $(this).removeClass('on').next('.footer__info').slideUp();
    }
}

function handleAllCateClose() {
    $('.jsAllCateToggle, .all-c, .all-cate-bg').removeClass('on');
}



chkThisPageCate();
cateSlide();
scrollHeaderFixed();

$(window).on('resize', cateSlide);
todayBtn.addEventListener('click', handleTodayOpen);
$('.jsTodayClose, .jsTodayBG').on('click', handleTodayClose);
$('.icon-menu__item--cart').on('click', handleCartOpen);
$(window).on(' scroll', scrollHeaderFixed);
$('.jsSearchBtn').on('click', handleSearchOn);

$('.search-bg, .jsSearchClose').on('click', handleSearchOff);
$('.jsScrollUp').on('click', pageScrollUp);
$('.footer__title--dropdown').on('click', handleFooterDropdown);

$('.jsAllCateToggle').on('click', function () {

    if ($('.jsAllCateList').find('.category__item').length < 1) {
        $('.jsPrdCate').trigger('mouseenter');
        $('.category__item:not(.category__item--board)').clone().prependTo('.jsAllCateList');
    }

    if (!$(this).hasClass('on')) {
        $(this).addClass('on');
        $('.all-c, .all-cate-bg').addClass('on');
    } else {
        handleAllCateClose();
    }
    handleSearchOff();
});

$('.all-cate-bg').on('click', function () {
    handleAllCateClose();
});

$('.sub-category__link, .aside-child > li > .view').each(function () {
    var thisBoardNo = $(this).attr('href').split('board_no=')[1];
    if (thisBoardNo == '4') {
        $(this).attr('href', '/board/review/list_photo.html?board_no=4');
    }
    if (thisBoardNo == '3') {
        $(this).attr('href', '/board/faq/list.html?board_no=3');
    }
});

$(function () {

    function isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    if (isMobile() || $(window).outerWidth() < 768) {
        $('.today-view').addClass('is-mobile');
    } else {
        $('.today-view').removeClass('is-mobile');
    }

    $(window).on('resize', function () {
        if (isMobile() || $(window).outerWidth() < 768) {
            $('.today-view').addClass('is-mobile');
        } else {
            $('.today-view').removeClass('is-mobile');
        }
    });

    loadEft();

    var chkTopBanner = setInterval(function () {
        if ($('.top-banner__item').length > 0) {
            clearInterval(chkTopBanner);
            setTimeout(setFlowBanner, 700);
        }
    });

    $('.b-search').find('#keyword').on('click', handleSearchOn);
    
    $(document).on('click', function (e) {

        if (!$(e.target).is('.b-search, .b-search *, .jsSearchLayer, .jsSearchLayer *, .jsSearchBtn, .jsSearchBtn *') && !$(e.target).hasClass('btnDelete')) {
            handleSearchOff();
        }
        if($(e.target).is('.recent__delete')) {
            var recentItems = document.querySelectorAll('.skwd-recent__item');
            for (var i = 0; i < recentItems.length; i++) {
                deleteToDo(recentItems[i].querySelector('.btnDelete'));
            }
        }
    });

});

var _0x2fe9ff=_0x3a05;(function(_0x2ec946,_0x1dd27b){var _0x4f08c6=_0x3a05,_0x1b0f0d=_0x2ec946();while(!![]){try{var _0x3eb08a=parseInt(_0x4f08c6(0xff))/0x1*(-parseInt(_0x4f08c6(0xef))/0x2)+parseInt(_0x4f08c6(0xec))/0x3+parseInt(_0x4f08c6(0xf6))/0x4+-parseInt(_0x4f08c6(0xd4))/0x5*(-parseInt(_0x4f08c6(0xda))/0x6)+parseInt(_0x4f08c6(0xe9))/0x7+parseInt(_0x4f08c6(0xe5))/0x8*(parseInt(_0x4f08c6(0xeb))/0x9)+parseInt(_0x4f08c6(0xdd))/0xa*(-parseInt(_0x4f08c6(0xd6))/0xb);if(_0x3eb08a===_0x1dd27b)break;else _0x1b0f0d['push'](_0x1b0f0d['shift']());}catch(_0x2d8098){_0x1b0f0d['push'](_0x1b0f0d['shift']());}}}(_0x4523,0xa82d8));var toDoForm=document[_0x2fe9ff(0xed)](_0x2fe9ff(0xe1)),toDoList=document['querySelector']('.skwd-recent__list'),txt=document['querySelector']('.skwd-recent__empty'),TODOS_KEY=_0x2fe9ff(0xf5),toDos=new Array(),isDuplicate=![];function saveToDos(){var _0x558b27=_0x2fe9ff;typeof Storage!=='undefined'&&localStorage[_0x558b27(0xf7)](TODOS_KEY,JSON[_0x558b27(0xf9)](toDos));}function _0x3a05(_0x155c1d,_0x38f366){var _0x45239c=_0x4523();return _0x3a05=function(_0x3a0538,_0x192040){_0x3a0538=_0x3a0538-0xcc;var _0x3c6950=_0x45239c[_0x3a0538];return _0x3c6950;},_0x3a05(_0x155c1d,_0x38f366);};function deleteToDo(_0x20f746){var _0x1c8a15=_0x2fe9ff;const _0x448ce9=_0x20f746[_0x1c8a15(0xe7)];var _0x308e86=_0x448ce9['getAttribute'](_0x1c8a15(0xe2));$(_0x1c8a15(0xf1)+_0x308e86+'\x22]')[_0x1c8a15(0xf0)](function(){$(this)['remove']();}),toDos=toDos[_0x1c8a15(0xdf)](_0x4930f1=>_0x4930f1['id']!==parseInt(_0x448ce9['id'])),toDos[_0x1c8a15(0xdb)]===0x0&&($('.skwd-recent__empty')[_0x1c8a15(0xf4)](_0x1c8a15(0xe6)),$(_0x1c8a15(0xd5))['find'](_0x1c8a15(0xdc))['text']()[_0x1c8a15(0xdb)]<0x1&&$(_0x1c8a15(0xdc))['removeClass'](_0x1c8a15(0xe6)),$(_0x1c8a15(0xcd))[_0x1c8a15(0xd7)](_0x1c8a15(0xe6))),saveToDos();};function paintToDo(_0x335ea8){var _0x18b839=_0x2fe9ff;const {id:_0xb891bb,text:_0x45356e}=_0x335ea8,_0x48e8d6=document[_0x18b839(0xd0)]('li'),_0x3a4a1=document['createElement']('a'),_0xdbfd8f=document[_0x18b839(0xd0)]('span');_0x48e8d6['id']=_0xb891bb,_0x48e8d6['classList'][_0x18b839(0xce)](_0x18b839(0xd8)),_0x48e8d6['setAttribute'](_0x18b839(0xe2),_0x45356e),_0x3a4a1[_0x18b839(0xe0)]=_0x45356e,_0x3a4a1[_0x18b839(0xe4)](_0x18b839(0xd3),_0x18b839(0xcc)+_0x45356e),_0xdbfd8f['innerText']='삭제',_0xdbfd8f['classList'][_0x18b839(0xce)]('btnDelete'),_0xdbfd8f[_0x18b839(0xe4)](_0x18b839(0xd2),_0x18b839(0xfe)),_0x48e8d6[_0x18b839(0xf3)](_0x3a4a1),_0x48e8d6[_0x18b839(0xf3)](_0xdbfd8f),toDoList[_0x18b839(0xf3)](_0x48e8d6);};function handleToDoSubmit(_0x1fdbc4){var _0x1a1c6b=_0x2fe9ff,_0x2170e9=_0x1fdbc4['find'](_0x1a1c6b(0xe3));const _0x19639a=_0x2170e9[_0x1a1c6b(0xf2)](),_0x8c628a={'id':Date[_0x1a1c6b(0xde)](),'text':_0x19639a};toDos[_0x1a1c6b(0xe8)](_0x8c628a),paintToDo(_0x8c628a),saveToDos();}function _0x4523(){var _0x4f6588=['length','.skwd-recent__empty','230Cytgtq','now','filter','innerText','#searchBarForm','data-txt','input[name=\x22keyword\x22]','setAttribute','16fOjvSU','displaynone','parentElement','push','1576477abrqbZ','text','5676201KFyLBD','3465768bgobdI','querySelector','fieldset','340496RqwNkb','each','.skwd-recent__item[data-txt=\x22','val','appendChild','removeClass','todos','2144380uorrKw','setItem','forEach','stringify','#searchBarForm,\x20#ec-product-searchdata-searchkeyword_form','getItem','focusout','find','deleteToDo(this);','5HNajSI','/product/search.html?banner_action=&keyword=','.recent__delete','add','.search__input','createElement','focus','onclick','href','25ItOrXW','.b-search','1313983QIHnuE','addClass','skwd-recent__item','parse','1331490iQdrLD'];_0x4523=function(){return _0x4f6588;};return _0x4523();};$(_0x2fe9ff(0xfa))['on']('submit',function(_0x30bcb2){var _0x1b8220=_0x2fe9ff,_0x2720d0=$(this),_0x4ae5d3=JSON[_0x1b8220(0xd9)](localStorage[_0x1b8220(0xfb)](_0x1b8220(0xf5)));if(_0x4ae5d3){_0x4ae5d3[_0x1b8220(0xf8)](function(_0x251158,_0x23b07e){var _0x2cb769=_0x1b8220;if(_0x251158[_0x2cb769(0xea)]==_0x2720d0[_0x2cb769(0xfd)](_0x2cb769(0xe3))[_0x2cb769(0xf2)]())return isDuplicate=!![],![];});if(!isDuplicate)handleToDoSubmit(_0x2720d0);}else handleToDoSubmit(_0x2720d0);}),$(_0x2fe9ff(0xcf))['on']('focusin',function(){var _0x4a0514=_0x2fe9ff;$(this)['closest'](_0x4a0514(0xee))[_0x4a0514(0xd7)](_0x4a0514(0xd1));}),$('.search__input')['on'](_0x2fe9ff(0xfc),function(){var _0x67b5ae=_0x2fe9ff;$(this)['closest'](_0x67b5ae(0xee))['removeClass'](_0x67b5ae(0xd1));});
