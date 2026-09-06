document.addEventListener('DOMContentLoaded', function () {
    const config = priceConfigs;
    const prices = config.prices;
    const title = config.title;

    const container = document.querySelector('.ds_benefit');
    if (container) container.style.display = 'none'; // 렌더링 전 숨기기

    const priceEl = document.getElementById('span_product_price_text');
    if (!priceEl) return;

    // 원가 숫자 추출
    let priceText = priceEl.textContent.trim();
    let priceStr = priceText.includes('(') ? priceText.split('(')[0] : priceText;
    let basePrice = parseInt(priceStr.replace(/[^0-9]/g, ''), 10);

    if (isNaN(basePrice)) return;

    function checkNoPricesDisplayY() {
        return Object.values(priceConfigs.prices).every(price => {
            const element = document.querySelector(`${price.className} td span`);
            if (!element) {
                console.log(`❌ Element not found: ${price.className}`);
                return true;
            }
            const text = element.innerText.trim().toUpperCase();
            /*
            console.log(element.innerText);
            console.log(`✅ Checking ${price.className}: "${text}"`);
            */
            return text !== 'Y';
        });
    }
    
    if (checkNoPricesDisplayY()) return;

    // 기존 리스트 영역 초기화
    const listContainer = container.querySelector('.ds_benefit_list');
    listContainer.innerHTML = '';

    // 가격 항목 렌더링
    let lowestPrice = Infinity;
    Object.keys(prices).forEach(function (key) {
        const data = prices[key];

        if(document.querySelector(`${data.className}`)&&document.querySelector(`${data.className} td span`).textContent.trim().toUpperCase()=='Y'){
            const finalPrice = basePrice - data.coupon.discount;
            if (finalPrice < lowestPrice) lowestPrice = finalPrice;

            const item = document.createElement('div');
            item.className = `item ${key}`;
            item.style.backgroundColor = `${data.bgColor}`;
            item.innerHTML = `
                <div class="item_title">
                    <div class="title">
                    	<img src="${data.title.icon}" alt="${data.title.label}">
                    	<span style="color:${data.title.color};">${data.title.label}</span>
                    </div>
                    <div class="coupon">
                    	<strong class="price" style="color:${data.coupon.color};">
                    		<span class="value">${data.coupon.discount.toLocaleString()}</span>
							<span class="unit">원</span>
							<span class="text">쿠폰</span>
                    	</strong>
                    </div>
				</div>
				<div class="item_price">
                    <strong class="price" style="color:${data.price.color};">
                    	<span class="value">${finalPrice.toLocaleString()}</span>
                    	<span class="unit">원</span>
                    </strong>
                </div>
            `;

            listContainer.appendChild(item);
        }
    });

    // 최대 혜택가 영역 렌더링
    const benefitMaxEl = container.querySelector('.ds_benefit_max');
    if (benefitMaxEl) {
        benefitMaxEl.innerHTML = `
            <strong class="title" style="color:${title.color};">
            	${title.label}
            </strong>
            <strong class="price" style="color:${title.price.color};">
            	<span class="value">${lowestPrice.toLocaleString()}</span>
            	<span class="unit">원</span>
            </strong>
		`;
    }

    if (container) container.style.display = ''; // 렌더링 후 표시

    function customOptionList(){
        console.log('%c------------custom option start------------','color:red');
        const trElements = document.querySelectorAll('.xans-product-detaildesign.detail-spec table tbody tr[class*="custom_option"]');

        trElements.forEach(tr => {
            const relValue = tr.getAttribute('rel') || 'none rel';
            const classList = tr.className.split(' ');
            const firstClass = classList.length > 0 ? classList[1] : 'none class';
            console.log(`${relValue}: ${firstClass}`);
        });
        console.log('%c------------custom option end------------','color:red');
    }
    customOptionList();
});
