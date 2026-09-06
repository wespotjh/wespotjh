# -*- coding: utf-8 -*-
"""장바구니 프리뷰용 목업 생성기.
   order/basket.html 의 {$변수} 를 그럴듯한 값으로 치환해 실제 렌더 DOM 을 재현한다.
   값은 전부 가짜다 — 화면 확인용이며 라이브와 무관하다."""
import io, re, os

SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = io.open(os.path.join(SK, 'order', 'basket.html'), encoding='utf-8').read()

# 스킨 디렉티브 제거
src = re.sub(r'<!--@(layout|css|js|import)\([^)]*\)-->', '', src)
# 주석 제거(우리가 넣은 설명 주석 포함)
src = re.sub(r'<!--(?!\[if).*?-->', '', src, flags=re.S)


def find_block(html, start_tag):
    """start_tag 로 시작하는 div 의 짝이 맞는 닫는 태그까지를 잘라 낸다."""
    i = html.index(start_tag)
    depth = 0; j = i
    while True:
        no = html.find('<div', j); nc = html.find('</div>', j)
        if nc == -1: raise ValueError('닫는 태그 없음')
        if no != -1 and no < nc:
            depth += 1; j = no + 4
        else:
            depth -= 1; j = nc + 6
            if depth == 0: return i, j

ITEMS = [
  dict(name='젠제네틱스 포타슘 칼륨 (20ea)', opt='1박스 · 20포', price='34,900원',
       sum='34,900원', qty='1', mileage='349원', delv='3,500원'),
  dict(name='[칼마비 건강루틴] 칼륨 + 마그네슘 + 비타민B컴플렉스 SET', opt='기본',
       price='107,500원', sum='107,500원', qty='1', mileage='1,075원', delv='무료'),
]

def render_row(it, i):
    V = {
      'chk_id':'chk%d'%i, 'chk_name':'idx[]', 'param':'?product_no=11',
      'img':'https://zengenetics.co.kr/web/product/small/thumb.jpg',
      'prod_id':'prd%d'%i,
      'product_name_link':'<a href="/product/detail.html">%s</a>'%it['name'],
      'icon':'', 'today_arrival_icon':'', 'pickup_icon':'', 'benefit_icons':'',
      'product_purchase_price_div_id':'pp%d'%i,
      'product_purchase_price_front_head':'', 'product_purchase_price_front':it['price'],
      'product_purchase_price_front_tail':'',
      'product_purchase_price_back_head':'', 'product_purchase_price_back':'',
      'product_purchase_price_back_tail':'',
      'sum_price_front_head':'', 'sum_price_front':it['sum'], 'sum_price_front_tail':'',
      'sum_price_back_head':'', 'sum_price_back':'', 'sum_price_back_tail':'',
      'product_discount_price_id':'dp%d'%i,
      'product_discount_price_front_head':'', 'product_discount_price_front':'0원',
      'product_discount_price_front_tail':'',
      'product_discount_price_back_head':'', 'product_discount_price_back':'',
      'product_discount_price_back_tail':'',
      'delv_price_front_head':'', 'delv_price_front':it['delv'], 'delv_price_front_tail':'',
      'delv_price_back_head':'', 'delv_price_back':'', 'delv_price_back_tail':'',
      'delv_type':'선불', 'product_delv_str':'3,500원 (5만원 이상 무료)',
      'subscription_option_str':'', 'product_mileage_id':'mi%d'%i, 'mileage':'적립금 '+it['mileage'],
      'product_weight':'0.05', 'quantity':it['qty'], 'total_product_weight':'0.05',
      'product_name':it['name'], 'option_str':it['opt'], 'qty':it['qty'],
      'action_option_change':'return false;', 'action_modify':'return false;',
      'add_shortcut':'return false;', 'out_shortcut':'return false;',
      'action_wish_item':'return false;', 'action_buy_item':'return false;',
      'action_move_item':'return false;',
      'form.quantity':'<input type="text" class="quantity" value="%s" size="3">'%it['qty'],
      'discount':'',
    }
    HIDE = ['exclusive_purchase_olny','subscription_show_display','product_weight_display',
            'nplusevent_show_display','product_discount_cnt_display',
            'product_purchase_price_display','sum_price_display','delv_ref_display',
            'product_discount_price_ref_display','subscription_hide_display',
            'product_name_display','option_change_display','delv_price_display',
            'qty_display','nplusevent_hide_display']
    a, bnd = find_block(src, '<div module="Order_list">')
    row = src[a:bnd]
    def sub(x):
        key = x.group(1)
        if '|display' in key:
            k = key.split('|')[0]
            if k in ('nplusevent_show_display','subscription_show_display','exclusive_purchase_olny',
                     'product_weight_display','product_discount_cnt_display','subscription_hide_display',
                     'product_purchase_price_display','sum_price_display','delv_ref_display',
                     'product_discount_price_ref_display','product_name_display'):
                return 'displaynone'
            return ''
        return V.get(key, '')
    return re.sub(r'\{\$([^}]+)\}', sub, row)

rows = ''.join(render_row(it, i) for i, it in enumerate(ITEMS))
a, bnd = find_block(src, '<div module="Order_list">')
out = src[:a] + rows + src[bnd:]

TOT = {
 'item_total':'2', 'basket_count':'2', 'basket_oversea_count':'0',
 'basket_remove_perd':'30', 'domestic_select':'selected',
 'total_product_price_display_front_head':'', 'total_product_price_display_front':'142,400원',
 'total_product_price_display_front_tail':'',
 'total_product_base_display':'129,455원', 'total_product_vat_display':'12,945원',
 'total_delv_price_front_head':'', 'total_delv_price_front':'0원', 'total_delv_price_front_tail':'',
 'total_delv_price_front_id':'tdp', 'shipfee_condition':'5만원 이상 무료배송',
 'shipfee_layer_id':'sfl', 'shipfee_sale_title':'무료배송', 'shipfee_benefit_use_condition':'',
 'total_benefit_price_title_area_id':'tbt', 'total_benefit_price_area_id':'tba',
 'total_benefit_list_id':'tbl',
 'total_product_discount_price_front_head':'', 'total_product_discount_price_front':'0원',
 'total_product_discount_price_front_tail':'', 'total_product_discount_price_front_id':'tpd',
 'total_order_price_front_head':'', 'total_order_price_front':'142,400원',
 'total_order_price_front_tail':'', 'total_order_price_front_id':'top',
 'card_img':'', 'total_weight':'0.1',
 'action_delete':'return false;','action_estimate':'return false;',
 'action_order_store_pickup_select':'return false;',
 'action_order_all':'return false;','action_order_select':'return false;',
 'naver_checkout_button_id':'nvchk','app_payment_button_box_id':'apppay',
 'param':'', 'product_name':'', 'layer_option_str':'', 'option_name':'',
 'form.option_value':'<select><option>선택</option></select>',
}
HIDE_TOT = ['oversea_display','total_cash_on_delv_msg_deisplay',
            'total_benefit_layer_display','vat_total_display','order_shipfee_sale_info_display',
            'total_product_price_ref_display','total_delv_price_ref_display',
            'total_product_discount_price_ref_display','total_order_price_ref_display',
            'shipping_info_show_display','basket_price_info_guide_display',
            'action_order_store_pickup_select_display','total_weight_display',
            'min_price_display','shipfee_benefit_date_title_display',
            'shipfee_benefit_member_condition_display','basket_price_sale_guide_display']
def sub2(x):
    key=x.group(1)
    if '|display' in key:
        k=key.split('|')[0]
        return 'displaynone' if k in HIDE_TOT else ''
    return TOT.get(key,'')
out = re.sub(r'\{\$([^}]+)\}', sub2, out)
out = out.replace('<p module="Order_Empty" class="ec-base-prdEmpty">',
                  '<p module="Order_Empty" class="ec-base-prdEmpty displaynone">')

CSS = ['layout/basic/css/common.css','layout/basic/css/layout.css','layout/basic/css/ec-base-ui.css',
 'layout/basic/css/ec-base-button.css','layout/basic/css/ec-base-tab.css','layout/basic/css/ec-base-table.css',
 'layout/basic/css/ec-base-tooltip.css','layout/basic/css/ec-base-help.css','layout/basic/css/ec-base-fold.css',
 'layout/basic/css/ec-base-box.css','layout/basic/css/ec-base-desc.css','layout/basic/css/ec-base-product.css',
 'layout/basic/css/ec-base-prdInfo.css','layout/basic/css/ec-base-paginate.css','layout/basic/css/ec-base-layer.css',
 'moa/css/lib/default.css','moa/css/layout.css','css/module/order/basketPackage.css']

def page(extra_css):
    links = '\n'.join('<link rel="stylesheet" href="../../%s">'%c for c in CSS)
    if extra_css:
        links += '\n<link rel="stylesheet" href="../../%s">'%extra_css
        links += '\n<script defer src="../../ds/js/basket.js"></script>'
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>장바구니 프리뷰</title>\n' + links +
            '\n<style>body{margin:0;background:#fff}#contents{max-width:1120px;margin:0 auto;padding:20px}'
            '.displaynone{display:none!important}</style>'
            '</head><body><div id="contents">' + out + '</div></body></html>')

io.open(os.path.join(SK,'_preview','basket','before.html'),'w',encoding='utf-8').write(page(None))
io.open(os.path.join(SK,'_preview','basket','after.html'),'w',encoding='utf-8').write(page('ds/css/basket.css'))
print('목업 생성 완료 · 상품행 %d개'%len(ITEMS))
