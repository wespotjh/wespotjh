
let customOption3,customOption3_title,customOption4,customOption4_title;
/* const customOption3 = document.querySelector('.custom_option3');
const customOption4 = document.querySelector('.custom_option4');
const customOption3_title = customOption3.querySelector('strong.title') ? customOption3.querySelector('strong.title').textContent.replace(':', '').trim() : '';
const customOption4_title = customOption4.querySelector('strong.title') ? customOption4.querySelector('strong.title').textContent.replace(':', '').trim() : ''; */

/* customOption3 = document.querySelector('.spec li.custom_option3') ? document.querySelector('.spec li.custom_option3') : document.querySelector('tr.custom_option3_css');
customOption4 = document.querySelector('.spec li.custom_option4') ? document.querySelector('.spec li.custom_option4') : document.querySelector('tr.custom_option4_css');

customOption3_title = customOption3.querySelector('strong.title') ? customOption3.querySelector('strong.title').textContent.replace(':', '').trim() : customOption3.querySelector('th span').textContent.trim();
customOption4_title = customOption4.querySelector('strong.title') ? customOption4.querySelector('strong.title').textContent.replace(':', '').trim() : customOption4.querySelector('th span').textContent.trim(); */

customOption3 = document.querySelector('.spec li.custom_option3') || document.querySelector('tr.custom_option3_css');
customOption4 = document.querySelector('.spec li.custom_option4') || document.querySelector('tr.custom_option4_css');

if (!customOption3 || !customOption4) {
    customOption3_title = '회원가';
    customOption4_title = '플친가';
} else {
    customOption3_title = customOption3.querySelector('strong.title') 
        ? customOption3.querySelector('strong.title').textContent.replace(':', '').trim() 
        : customOption3.querySelector('th span')
            ? customOption3.querySelector('th span').textContent.trim()
            : '회원가';
            
    customOption4_title = customOption4.querySelector('strong.title')
        ? customOption4.querySelector('strong.title').textContent.replace(':', '').trim()
        : customOption4.querySelector('th span')
            ? customOption4.querySelector('th span').textContent.trim()
            : '플친가';
}


const priceConfigs = {
    title: {
        label: '최대 혜택가',
        color: '#111', // 라벨 글자 색상
        price: {
        	color: '#ff0000', // 금액 글자 색상
        }
    },
    prices: {
        // 회원 특가
        member: {
            className: '.custom_option3_css',  // 상품상세 페이지중 회원가 클래스명
            listClassName: '.custom_option3',  // 메인, 상품분류 페이지중 회원가 클래스명
            bgColor: 'rgb(14 46 114)', // 배경색
            title: {
                icon: 'https://wespotjo.cafe24.com/ds/image/ico_price1.png',
            	label: customOption3_title, //회원 특가
                color: '#fff',     // 상품상세 페이지중의 글자 색상
                listColor: '#fff', // 메인, 상품분류 페이지중의 글자 색상
            },
            coupon: {
            	discount: 2000,    // 쿠폰 금액
                label: '쿠폰',
                color: '#fff',     // 상품상세 페이지중의 글자 색상
                listColor: '#000', // 메인, 상품분류 페이지중의 글자 색상
            },
            price: {
                color: '#fff',     // 상품상세 페이지중의 글자 색상
                listColor: '#000', // 메인, 상품분류 페이지중의 글자 색상
            },
        },
        // 플친 특가
    	friend: {
            className: '.custom_option4_css',  // 상품상세 페이지중 플친가 클래스명
            listClassName: '.custom_option4',  // 메인, 상품분류 페이지중 플친가 클래스명
            bgColor: 'rgb(254 221 44)', // 배경색
            title: {
                icon: 'https://wespotjo.cafe24.com/ds/image/ico_price2.webp',
            	label: customOption4_title,  //플친 특가
                color: '#222',     // 상품상세 페이지중의 글자 색상
                listColor: '#222', // 메인, 상품분류 페이지중의 글자 색상
            },
            coupon: {
            	discount: 20100,    // 쿠폰 금액
                label: '쿠폰',
                color: '#222',     // 상품상세 페이지중의 글자 색상
                listColor: '#000', // 메인, 상품분류 페이지중의 글자 색상
            },
            price: {
                color: '#222',     // 상품상세 페이지중의 글자 색상
                listColor: '#000', // 메인, 상품분류 페이지중의 글자 색상
            },
        },
    }
};
