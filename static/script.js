var flgWaitForState = false;
var flgWaitForMove = false;

function init() {
    render_field()
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
//    'height': высота
//    'width': ширина
//    'labyrinth': лабиринт
//    'hero': позиция героя
//    'ninja': позиция ниндзя

    TableDrop();

    let table_head = document.getElementById('id_game_table').getElementsByTagName('thead')[0];
    tr = table_head.insertRow();
    for (let j = 0; j < col; j++) {
        th = document.createElement('th');
        // th.classList = "tdicon";
        th.width = 30;
        tr.appendChild(th);
    }

    let table_body = document.getElementById('id_game_table').getElementsByTagName('tbody')[0];
    for (let i = 0; i < row; i++) {
        tr = table_body.insertRow(i);
        for (let j = 0; j < col; j++) {
            td = tr.insertCell();
//            td.id = 'td_' + i + '_' + j
            if (labyrinth[i][j] === 'X') {
                td.classList = 'cell-wall';
            } else {
                td.classList = 'cell';
            }

            //   x ---
            // y
            // |
            // |
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
            // td.style.border = '1px solid black';
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
        url += direct
        get_json(url, null, move_onload, move_onerror);
    }
}

function move_onload(status, json) {
    render_field()
    flgWaitForMove = false;
}

function move_onerror(status, json) {
    flgWaitForMove = false;
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

function render_field_onload(status, json) {
    const data = JSON.parse(json);

    // обработка в случае отсутствия данных или ошибки
    if (!data || data.status == 'error') {
        const elemModal = document.querySelector('#id_modal_error');

        elemModal.addEventListener('hidden.bs.modal', function(e) {
          console.log("Modal closed 1");
          window.location.href = "/index.html";
        });

        var myModal = new bootstrap.Modal(document.getElementById('id_modal_error'));
        myModal.show();
    }

    if (data.status == 'stop') {
        // TODO обработчик stop
    }

// TODO добавить номер шага ((( data.step

    if (data) {
        TableDraw(data.width, data.height, data.labyrinth, data.hero, data.ninja);
        setStatusOK();
    }

    flgWaitForState = false;

    if (data['game_status'] == 'end'){
        const elemModal = document.querySelector('#id_modal_end');

        var myModal = new bootstrap.Modal(document.getElementById('id_modal_end'));
        myModal.show();
        // alert('Конец игры. You ' + data['game_result'])

        button_change_status(true)
    } else {
        button_change_status(false)
    }
}

function render_field_onerror(status) {
    TableDrop();
    setStatusError();
    flgWaitForState = false;
}

function setStatusOK() {
    // TODO
}

function setStatusError() {
    // TODO
}

init()
