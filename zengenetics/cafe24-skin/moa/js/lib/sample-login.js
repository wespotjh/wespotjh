var sampleName = document.getElementById('sample-name');

if (sampleName.innerHTML == '바디랩' || sampleName.innerHTML == 'moa' || sampleName.innerHTML == '모아' || sampleName.innerHTML == 'moa-studio') {
    var fakeLogin = document.querySelectorAll('.fake-sns-login');
    fakeLogin[0].classList.remove('displaynone');
    if(fakeLogin[1]) fakeLogin[1].classList.remove('displaynone');
}

$(function () {

    $('.jsSampleBtn').on('click', function (e) {
        alert('관리자 설정을 통해 간편 로그인 사용이 가능합니다.');
        e.preventDefault();
    });
    
});

window.onload = function() {
    document.getElementById('member_passwd').setAttribute('placeholder', '비밀번호');
}