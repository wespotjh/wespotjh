/**
 * 카테고리 마우스 오버 이미지
 * 카테고리 서브 메뉴 출력
 */

if(matchMedia("screen and (min-width: 1024px)").matches) {

    var eventTxtArr = ['이벤트', 'event', 'Event'];

    $(document).ready(function () {

        var cateData;
        var methods = {
            aCategory: [],
            aSubCategory: {},

            get: function () {
                $.ajax({
                    url: '/exec/front/Product/SubCategory',
                    dataType: 'json',
                    success: function (aData) {

                        cateData = aData;

                        if (aData == null || aData == 'undefined') return;
                        for (var i = 0; i < aData.length; i++) {
                            var sParentCateNo = aData[i].parent_cate_no;

                            if (!methods.aSubCategory[sParentCateNo]) {
                                methods.aSubCategory[sParentCateNo] = [];
                            }

                            methods.aSubCategory[sParentCateNo].push(aData[i]);
                        }

                    }
                });
            },

            getParam: function (sUrl, sKey) {

                var aUrl = sUrl.split('?');
                var sQueryString = aUrl[1];
                var aParam = {};

                if (sQueryString) {
                    var aFields = sQueryString.split("&");
                    var aField = [];
                    for (var i = 0; i < aFields.length; i++) {
                        aField = aFields[i].split('=');
                        aParam[aField[0]] = aField[1];
                    }
                }
                return sKey ? aParam[sKey] : aParam;
            },

            getParamSeo: function (sUrl) {
                var aUrl = sUrl.split('/');
                return aUrl[3] ? aUrl[3] : null;
            },

            show: function (overNode, iCateNo, iCateName) {

                if(methods.aSubCategory[iCateNo]) {
                    if (methods.aSubCategory[iCateNo].length == 0) {
                        return;
                    }


                    var aHtml = [];
                    aHtml.push('<ul class="sub-category__list">');
                    // event link
                    if(eventTxtArr.indexOf(iCateName) > 0) {
                        var getEventLink = $(methods.aSubCategory[iCateNo])[0].param;
                        overNode.find('a').attr('href', '/event/list.html' + getEventLink);
                        $(methods.aSubCategory[iCateNo]).each(function () {
                            aHtml.push('<li class="sub-category__item"><a class="sub-category__link eng-font jsChildTwo" href="/event/list.html' + this.param + '">' + this.name + '</a></li>');
                        });
                    }
                    else {
                        $(methods.aSubCategory[iCateNo]).each(function () {
                            aHtml.push('<li class="sub-category__item"><a class="sub-category__link eng-font jsChildTwo" href="' + this.link_product_list + '">' + this.name + '</a></li>');
                        });
                    }
                    aHtml.push('</ul>');


                    var offset = $(overNode).offset();
                    $('<div class="sub-category"></div>')
                        .appendTo(overNode)
                        .html(aHtml.join('')).addClass('on');
                    setTimeout(function() {
                        $(overNode).find('.sub-category').removeClass('on');
                    },200);
                }
            },

            close: function () {
                $('.sub-category').remove();
            }
        };

        methods.get();

        $('.xans-layout-category.category li.jsPrdCate').mouseenter(function (e) {
            var $this = $(this).addClass('on'),
                iCateNo = Number(methods.getParam($this.find('a').attr('href'), 'cate_no')),
                iCateName = $this.find('a').text();

            if (!iCateNo) {
                iCateNo = Number(methods.getParamSeo($this.find('a').attr('href')));
            }

            if (!iCateNo) {
                return;
            }
            if ($(this).find('.sub-category').length < 1) {
                methods.show($this, iCateNo, iCateName);
            }
        });


    });
    
}