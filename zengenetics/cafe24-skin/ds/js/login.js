document.addEventListener('DOMContentLoaded', function () {
    var trigger = document.querySelector('.eBtnOtherLogin');
    var target = document.querySelector('.eOtherLogin');

    trigger.addEventListener('click', function (e) {
        e.preventDefault();
        target.classList.add('show');
        trigger.classList.add('hide');
    });
});