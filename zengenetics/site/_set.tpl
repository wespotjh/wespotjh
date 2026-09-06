<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1"><style>@@CSS0@@</style></head><body>
<title>@@DOCTITLE@@</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>@@CSS1@@@@EXTRA@@</style>

<header class="gnb">
  <div class="in">
    <span class="back">&larr;</span>
    <span class="ttl">@@GNB@@</span>
    <span class="cart">CART</span>
  </div>
</header>

<div class="gal">
  <div class="rail" id="rail">
    <div class="sl"><img id="g1" alt="@@GNB@@ 세트"></div>
    <div class="sl"><img id="g2" alt="@@GNB@@ 구성"></div>
  </div>
  <div class="dots" id="dots"><i class="on"></i><i></i></div>
</div>

<div class="w head">
  <!-- cafe24: {$name} -->
  <div class="brand">@@BRAND@@</div>
  <h1>@@H1@@</h1>
  <!-- cafe24: {$simple_desc} -->
  <p class="sub">@@SUB@@</p>

  <!-- 리뷰는 알파리뷰 앱이 채운다. 숫자를 여기에 쓰지 않는다 (CLAUDE.md 규칙 13)
       cafe24 이식: <div class="alpha_widget" data-code="8d644bd9" data-value="{$product_no}"></div>
       이 상품의 product_no = @@PRDNO@@ -->
  <div class="rate"><a href="#reviews">고객 리뷰 보기 <span class="alpha_review_count"></span></a></div>

  <!-- cafe24: 할인율은 스킨 JS(calcDiscountPer)가 계산한다. % 를 타이핑하지 말 것 (규칙 11)
       .off = <span class="discount-per">, .now = {$product_price}, .was = {$product_custom} -->
  <div class="prow"><span class="off">@@OFF@@</span><span class="now">@@PRICE@@</span><span class="was">@@WAS@@</span></div>

  <div class="badges">@@BADGES@@</div>

  <div class="kit n@@KITN@@">@@KIT@@</div>
</div>

<!-- ── 하루 루틴 서사 (대표님 지시 2026-09-06) ── -->
<div class="rt">
 <div class="w">
  <span class="lab">Your routine</span>
  <h2>@@RTH2@@</h2>
  <p class="dek">@@RTDEK@@</p>
  <div class="tl">@@STEPS@@</div>
  <p class="foot">@@RTFOOT@@</p>
 </div>
</div>

<div class="w blk">
  <h2>수량</h2>
  <p class="hint">@@QTYHINT@@</p>
  <div class="qty">
    <button id="qm" aria-label="수량 줄이기">&minus;</button>
    <span id="qv">1</span>
    <button id="qp" aria-label="수량 늘리기">+</button>
  </div>
</div>

<div class="w blk">
  <h2>같이 담을까요?</h2>
  <p class="hint">고르시면 아래 합계에 바로 더해집니다. 따로 고르실 것은 없습니다.</p>
  <div class="adds" id="adds"></div>

  <div class="ship">
    <div class="t" id="shipT">&mdash;</div>
    <div class="bar"><i id="shipB"></i></div>
  </div>

  <div class="sum">
    <div class="r"><span>상품 금액</span><b id="sGoods">0원</b></div>
    <div class="r"><span>할인 금액</span><b id="sDisc">0원</b></div>
    <div class="r"><span>배송비</span><b id="sShip">0원</b></div>
    <div class="tot"><span>결제 예상 금액</span><b id="sTotal">0원</b></div>
  </div>
</div>

<div class="detail" id="reviews">
  <div class="w dh">
    <span class="lab">Product detail</span>
    <h2>@@DETAILH2@@</h2>
  </div>
  <div class="fold" id="fold">
    <div id="dimgs"></div>
    <div class="veil"><button class="more" id="moreBtn">상세 정보 모두 보기</button></div>
  </div>
</div>

<div class="w">
  <div class="acc">
    <details open><summary>배송</summary>
      <div class="a">세트는 금액이 5만원을 넘어 <b>배송비가 없습니다</b>.<br>
      평일 <b>오후 2시</b>까지 결제하시면 당일 출고됩니다. 주말과 공휴일은 다음 영업일에 나갑니다.</div></details>
    <details><summary>교환 &middot; 반품</summary>
      <div class="a">받으신 날부터 <b>7일 이내</b>에 고객센터(070-8872-1337)로 연락 주세요.<br>
      다만 개봉하셨거나 사용하신 제품, 그리고 포장이 훼손되어 다시 판매하기 어려운 경우에는 어려울 수 있습니다.</div></details>
    <details><summary>먹는 방법</summary>
      <div class="a">@@HOW@@<br>
      임신 중이거나 수유 중이신 분, 어린이, 약을 드시는 분은 미리 의사나 약사와 상의해 주세요.</div></details>
    <details><summary>세트 구성</summary>
      <div class="a">@@COMPOSE@@<br>
      자세한 원재료명과 영양정보는 위 상세 안내 하단의 제품 표시사항을 확인해 주세요.</div></details>
  </div>
  <p class="note">*화면 연출은 제품 이미지이며, 섭취에 따른 효과를 나타내지 않습니다<br>
  @@NOTE2@@<br>
  *평점과 리뷰 수는 알파리뷰 위젯이 집계해 표시합니다</p>
</div>

<div class="bar">
  <div class="in">
    <div class="sm"><i>결제 예상</i><b id="barTotal">0원</b></div>
    <button class="cart2" id="btnCart">장바구니</button>
    <button class="buy" id="btnBuy">구매하기</button>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>window.__STK__=@@STK@@;window.__HERO__=@@HERO@@;window.__DETAIL__=@@DET@@;</script>
<script>
(function(){
  "use strict";
  var S=window.__STK__, H=window.__HERO__, DT=window.__DETAIL__;
  var won=function(n){return n.toLocaleString('ko-KR')+'원'};
  var el=function(i){return document.getElementById(i)};

  el('g1').src=H[0]; el('g2').src=H[1];
  var rail=el('rail'), dots=el('dots').children;
  rail.addEventListener('scroll',function(){
    var i=Math.round(rail.scrollLeft/rail.clientWidth);
    for(var k=0;k<dots.length;k++) dots[k].classList.toggle('on',k===i);
  },{passive:true});

  @@KITJS@@
  @@STEPJS@@
  @@TYPEJS@@

  /* 가격 — cafe24 상품등록 값. 이식 시 {$product_price}/{$product_custom} 로 치환 */
  var SET=@@NPRICE@@, SETWAS=@@NWAS@@;
  var ADDS=@@ADDS@@;
  var FREE=50000, SHIPFEE=3500;
  var qty=1, picked={};

  var ac=el('adds');
  ADDS.forEach(function(a){
    var d=document.createElement('div');
    d.className='add'; d.setAttribute('role','checkbox'); d.dataset.id=a.id;
    d.innerHTML='<span class="box"><i>&#10003;</i></span>'+
      '<span class="th"><img alt=""></span>'+
      '<span><span class="nm">'+a.nm+'</span><span class="mt">'+a.mt+'</span></span>'+
      '<span class="pz">'+won(a.price)+'</span>';
    d.querySelector('img').src=S[a.img].v;
    d.addEventListener('click',function(){
      picked[a.id]=!picked[a.id];
      d.setAttribute('aria-checked', picked[a.id]?'true':'false');
      calc();
    });
    ac.appendChild(d);
  });

  function paintQty(){ el('qv').textContent=qty; el('qm').disabled=(qty<=1); }
  el('qm').addEventListener('click',function(){ if(qty>1){qty--;paintQty();calc();} });
  el('qp').addEventListener('click',function(){ if(qty<10){qty++;paintQty();calc();} });

  function calc(){
    var goods=SET*qty, listSum=SETWAS*qty;
    ADDS.forEach(function(a){ if(picked[a.id]){ goods+=a.price; listSum+=a.price; } });
    var disc=listSum-goods;
    var ship=(goods>=FREE)?0:SHIPFEE;
    el('sGoods').textContent=won(listSum);
    el('sDisc').textContent='−'+won(disc);
    el('sShip').textContent = ship? won(ship) : '무료';
    el('sTotal').textContent=won(goods+ship);
    el('barTotal').textContent=won(goods+ship);
    var t=el('shipT'), b=el('shipB');
    if(!ship){
      t.className='t done'; t.textContent='5만원을 넘겨서 배송비가 없습니다.';
      b.className='done'; b.style.width='100%';
    }else{
      t.className='t';
      t.innerHTML='<em>'+won(FREE-goods)+'</em> 더 담으시면 배송비가 없습니다.';
      b.className=''; b.style.width=Math.min(100,goods/FREE*100).toFixed(1)+'%';
    }
  }

  var dc=el('dimgs');
  DT.forEach(function(u,i){
    var im=document.createElement('img');
    im.src=u; im.alt=''; im.loading = i<2 ? 'eager':'lazy'; im.decoding='async';
    dc.appendChild(im);
  });
  el('moreBtn').addEventListener('click',function(){ el('fold').classList.add('open'); });

  var tm=0;
  function toast(msg){
    var t=el('toast'); t.textContent=msg; t.classList.add('on');
    clearTimeout(tm); tm=setTimeout(function(){ t.classList.remove('on'); },2200);
  }
  function summary(){
    var n=ADDS.filter(function(a){return picked[a.id]}).length;
    return '@@CARTNAME@@ '+qty+'개'+(n?' 외 '+n+'건':'');
  }
  /* cafe24 이식 시 onclick="{$action_basket}" / "{$action_buy}" 로 바뀐다 */
  el('btnCart').addEventListener('click',function(){ toast(summary()+'를 장바구니에 담았습니다'); });
  el('btnBuy').addEventListener('click',function(){ toast(summary()+' 구매로 넘어갑니다'); });

  paintQty(); calc();
})();
</script>

</body></html>
