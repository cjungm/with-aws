
const id = document.getElementById('id')
const password = document.getElementById('password')
let errStack = 0;

async function login() {
    let username = id.value;
    let userpw = password.value;
    let response = await $.get(apigatewayendpoint, { q: username, size: 25, action: "login" }, 'json');
    let results = response['hits']['hits'];
    if (results.length > 0) {
        if (results[0]._source.Password == userpw) {
            let email = results[0]._source.Email
            await alert(username + '님 환영합니다!')
            location.href = "search.html?username="+username;
        } else {
            alert('비밀번호를 다시 한 번 확인해주세요!')
            errStack ++;
        }
    } else {
        alert('존재하지 않는 계정입니다.')
    }

    if (errStack >= 5) {
        alert('비밀번호를 5회 이상 틀리셨습니다!')
        errStack = 0;
    }
}

async function enterkey() {
    if (window.event.keyCode == 13) {
        await login();
    }
}