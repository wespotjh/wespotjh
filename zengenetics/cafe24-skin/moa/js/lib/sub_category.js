if(matchMedia("screen and (min-width: 1024px)").matches) {

    function depthThree(target, cateNo) {
        var $cate = '';
        $.ajax({
            url: '/exec/front/Product/SubCategory',
            dataType: 'json',
            success: function (data) {
                $.each(data, function (m, key) {
                    if (key.parent_cate_no == cateNo) {
                        $cate += '<li class="sub-category__item"><a class="sub-category__link eng-font jsChildThree" href="/product/list.html' + key.param + '">' + key.name + '</a></li>';
                    };
                });
                if (target.next().length < 1 && $cate != '') {
                    target.each(function () {
                        $(this).after('<div class="sub-category sub-category--depth-three"><ul class="sub-category__list sub-category__list">' + $cate + '</ul></div>');
                    });
                    target.next('.sub-category').addClass('on');
                    setTimeout(function () {
                        target.next('.sub-category').removeClass('on');
                    }, 100);
                }
            }
        });
    }

    $(function () {

        $(document).on('mouseenter', '.jsChildTwo', function () {
            var getCateNo = $(this).attr('href').split('/')[3];
            depthThree($(this), getCateNo);
        });

        $(document).on('mouseenter', '.jsChildThree', function () {
            var getCateNo = $(this).attr('href').split('cate_no=')[1];
            depthThree($(this), getCateNo);
        });

    });
    
}