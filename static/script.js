var flgWaitForState = false;
var flgWaitForMove = false;

document.addEventListener("DOMContentLoaded", function(event){
    init();
})

function init() {
    render_field();
    window.addEventListener('keydown', e => checkArrow(e));
    document.getElementById('id_game_div').focus();
}

function checkArrow(e) {
    e = e || window.event;
    if (document.getElementById('id_game_div') == document.activeElement)
    {
        if (e.keyCode == '38') {
            Move('up')
            event.preventDefault()
        }
        else if (e.keyCode == '40') {
            Move('down')
            event.preventDefault()
        }
        else if (e.keyCode == '37') {
            Move('left')
        }
        else if (e.keyCode == '39') {
            Move('right')
        }
        else if (e.keyCode == '32') {
            Move('sleep')
        }
    }
}
function get_json(url, json=null, callback=null, callback_onerror=null) {
    // url              - url for request
    // callback         - function on load
    // json             - json to post on url
    // callback_onerror - function on error
    var xhr = new XMLHttpRequest();
    xhr.open(json !== null ? 'POST' : 'GET', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.responseType = 'json';
    if (callback) {
        xhr.onload = function () {
            callback(xhr.status, xhr.response);
        }
    }
    if (callback_onerror) {
        xhr.onerror = function() {
            callback_onerror(xhr.status);
        }
    }
    xhr.send(JSON.stringify(json));
}

function TableDrop() {
    let table = document.getElementById('id_game_table');

    let table_head = table.getElementsByTagName('thead')[0];
    table_head.remove();
    let table_body = table.getElementsByTagName('tbody')[0];
    table_body.remove();

    table.createTHead();
    table.createTBody();
}

function TableDraw(col, row, labyrinth, hero, ninja){
    TableDrop();

    let table_head = document.getElementById('id_game_table').getElementsByTagName('thead')[0];
    tr = table_head.insertRow();
    for (let j = 0; j < col; j++) {
        th = document.createElement('th');
        th.width = 30;
        tr.appendChild(th);
    }

    let table_body = document.getElementById('id_game_table').getElementsByTagName('tbody')[0];
    for (let i = 0; i < row; i++) {
        tr = table_body.insertRow(i);
        for (let j = 0; j < col; j++) {
            td = tr.insertCell();
            if (labyrinth[i][j] === 'X') {
                td.classList = 'cell-wall';
            } else {
                td.classList = 'cell';
            }

            if (i === hero[1] && j === hero[0]) {
                img = document.createElement("img");
                img.src = "static/hero.png";
                img.style.height = '30px';
                img.style.width = '30px';
                td.appendChild(img);
            }

            if (i === ninja[1] && j === ninja[0]) {
                img = document.createElement("img");
                img.src = "static/ninja.png";
                img.style.height = '30px';
                img.style.width = '30px';
                td.appendChild(img);
            }
        }
    }
}

function Move(direct){
    if (!flgWaitForMove && !flgWaitForState) {
        flgWaitForMove = true;
        if (direct == 'sleep') {
            url = '/action:'
        } else {
            url = '/move:'
        }
        url += direct;
        get_json(url, null, move_onload, move_onerror);
    }
}

function move_onload(status, json) {
    const data = JSON.parse(json);

    if (data && data['status'] === 'ok') {
        render_field();
        flgWaitForMove = false;
    }
}

function move_onerror(status, json) {
    flgWaitForMove = false;
    setStatusError();
}

function render_field() {
    if (!flgWaitForState) {
        flgWaitForState = true;
        get_json('/state', null, render_field_onload, render_field_onerror);
    }
}

function button_change_status(status) {
    for (let name of ['id_btn_up', 'id_btn_down', 'id_btn_left', 'id_btn_right', 'id_btn_sleep']){
        document.getElementById(name).disabled = status
    }
}

function show_modal_error(message) {
    // обработка закрытия с перенаправлением
    const elemModal = document.querySelector('#id_modal_error');
    elemModal.addEventListener('hidden.bs.modal', function(e) {
      window.location.href = "/index.html";
    });
    const elemInfo = document.querySelector('#id_text_error');
    elemInfo.innerHTML = "При получении данных произошла ошибка:<br><b>" + message + "</b>"

    var myModal = new bootstrap.Modal(document.getElementById('id_modal_error'));
    myModal.show();
}

function show_modal_info(title, message) {
    const elemTitle = document.querySelector('#idModalLabelInfo');
    elemTitle.innerHTML = title;
    const elemInfo = document.querySelector('#id_text_info');
    elemInfo.innerHTML = message;

    var myModal = new bootstrap.Modal(document.getElementById('id_modal_info'));
    myModal.show();
}

function render_field_onload(status, json) {
    const data = JSON.parse(json);

    // обработка в случае отсутствия данных или ошибки
    if (!data || data.status == 'error') {
        show_modal_error(data['message'])
    }

//    стоп обработаем при перерисовке игрового поля
//    if (data.status == 'stop') {
//    }

    if (data && data.status == 'ok') {
        TableDraw(data.width, data.height, data.labyrinth, data.hero, data.ninja);
        setStatusOK();
    }

    flgWaitForState = false;

    if (data['game_status'] == 'end'){
        button_change_status(true);

        if (data['game_result'] == 'win') {
            message = 'Поздравляем, <b>Вы победили</b>!<br><br>Еще разок? ;)'
        } else if (data['game_result'] == 'lose') {
            message = 'Поздравляем охотника, он большой молодец,<br>а <b>Вы проиграли</b>!<br><br>Еще разок? ;)';
        } else {
            message = 'Боевая ничья? Как добились? Сообщите разработчику!';
        }
        show_modal_info('Игра окончена.', message);
    } else {
        button_change_status(false);
    }
}

function render_field_onerror(status) {
    TableDrop();
    setStatusError();
    flgWaitForState = false;
}

function setStatusOK() {
    // nothing else
}

function setStatusError() {
    message = "Проблемы получения данных с сервера.<br>Подождите некоторое время и попробуйте повторно."
    show_modal_info("Ошибка получения данных", message);
}
