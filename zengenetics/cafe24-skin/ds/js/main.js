document.addEventListener('DOMContentLoaded', function () {
    const config = priceConfigs;
    const prices = config.prices;
    const title = config.title;

    const items = document.querySelectorAll('li[data-price]');

    items.forEach(li => {
        const basePrice = parseInt(li.getAttribute('data-price'), 10);
        if (isNaN(basePrice)) return;

        const container = document.createElement('div');
        container.className = 'ds_benefit';
        container.style.display = 'none';


        const listContainer = document.createElement('div');
        listContainer.className = 'ds_benefit_list';

        let lowestPrice = Infinity;

        Object.keys(prices).forEach(key => {
            const data = prices[key];
            
            const targetEl = li.querySelector(`${data.listClassName} > span`);
			const shouldShow = targetEl && targetEl.textContent.trim().toUpperCase() === 'Y';

            if (shouldShow) {
                const finalPrice = basePrice - data.coupon.discount;
                if (finalPrice < lowestPrice) lowestPrice = finalPrice;

                const item = document.createElement('div');
                item.className = `item ${key}`;

                item.innerHTML = `
                    <div class="item_price">
                  		<span class="item_title" style="background-color:${data.bgColor}; color:${data.title.listColor}">${data.title.label}</span>
                        <strong class="price" style="color:${data.price.listColor};">
                            <span class="value">${finalPrice.toLocaleString()}</span>
                            <span class="unit">원</span>
                        </strong>
                    </div>
                `;
                listContainer.appendChild(item);
            }
        });

        container.appendChild(listContainer);

        li.appendChild(container);

        if(li.querySelector('.custom_option3') || li.querySelector('.custom_option4')){
            container.style.display = '';
        }
    });
});
