

function init() {
    TableDrawBlank(30, 30);                  // draw table
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

function TableDrawBlank(col, row){
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
            td.id = 'td_' + i + '_' + j
            td.classList = 'cell';
            if (i === 6) {
                td.classList = 'cell-wall';
            }
            if (i === 1 && j === 1) {
                img = document.createElement("img");
                img.src = "static/favicon.ico";
                img.style.height = '30px';
                img.style.width = '30px';
                td.appendChild(img);
            }
            // td.style.border = '1px solid black';
        }
    }
}


//function TableDrawBlank(col, row) {
//    let table = document.getElementById('game_table');
//
//    // удаляем таблицу
//    // TableDrop();
//    // TODO сделать нормальную генерацию, а не вставлять в позицию 0.
//    // генерируем заново
//    for (var i = row - 1; i >= 0; i--) {
//        let x = table.insertRow(0);
//        for (var j=0; j < col; j++) {
//            table.rows[0].insertCell(j);
//            table.rows[0].cells[j].id = 'td' + i + '_' + j
//            table.rows[0].cells[j].classList = 'cell living-cell';
//            // table.rows[0].cells[j].style.cssText = 'width: 1%';
//        }
//    }
//    alert("I am an alert box!");
//}

init()