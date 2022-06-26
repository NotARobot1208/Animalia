var socket;
var sid = ""
var code;
for(i = 0; i < document.cookie.split(";").length; i++){
    if ('session' == document.cookie.split(";")[i].split("=")[0])    {
        sid = document.cookie.split(";")[i].split("=")[1]
        break
    }
}
$(document).ready(function(){
    param = new URLSearchParams(window.location.search);
    if (param.has('gameid')){
        joinGame(param.get("gameid"));
        return
    }
    $("#modal").modal({backdrop: 'static', keyboard: false});
});



function newChatSocket(){
    chatSocket = new WebSocket("wss://chat.animaliaga.me");
    
    chatSocket.onmessage = function(event){
        data = JSON.parse(event.data)
        d = document.createElement("p");
        d.classList.add('chatMsg');
        d.classList.add('yourChat');
        d.classList.add('moreMargin');
        d.appendChild(document.createTextNode(`${data['msg_author']} - ${data['msg_content']}`))
        cmsgs = document.querySelector("#chatMsgs")
        cmsgs.appendChild(d)
        cmsgs.scrollTo(0, cmsgs.scrollHeight);
        
        cmsgs.children[cmsgs.children.length-2].classList.toggle("moreMargin")
    }

    chatSocket.onopen = function(e){
        document.querySelector("#status").innerHTML = 'Status: Online'
        document.querySelector("#status").style.color = 'green'
    }
    
    chatSocket.onclose = function(e){
        document.querySelector("#status").innerHTML = 'Status: Offline'
        document.querySelector("#status").style.color = 'red'
    }

    return chatSocket
}
chatSocket = newChatSocket();
window.setInterval(function(){
    if (!(chatSocket.readyState === chatSocket.OPEN)){
        chatSocket = newChatSocket();
    }
}, 10000)

function subChat(){
    var inp = document.querySelector("textarea")
    if(inp.value == ''){ return }
    chatSocket.send(JSON.stringify({'msg_content': inp.value, 'msg_author_cookie': sid}));
    inp.value = '';
}



document.querySelector('textarea').addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    subChat()
  }
});



function joinGame(codeOrUrl){
    gameOver = false;
    code = codeOrUrl
    if (codeOrUrl.includes('?gameid=')){
        code = codeOrUrl.split("?gameid=")[1].split("&")[0]
    }
    document.querySelector("#gameid").innerText = "Game ID: " + code
    document.querySelector("#inviteLink").parentElement.remove()
    document.querySelector("#reopen").parentElement.remove()
    $("#modal").modal('hide');
    
    socket = new WebSocket("wss://ws.animaliaga.me");

    socket.onmessage = function(event) {
        data = JSON.parse(event.data)

        
        d = document.createElement('div');
        d.classList.add('bubble-opponent')
        if (Object.keys(data).includes("scores")){
            u1 = Object.keys(data['scores'])[0]
            u2 = Object.keys(data['scores'])[1]
            d.innerHTML = `<h4>Current Scores</h4><hr><h6>${u1} - ${data['scores'][u1]}</h6><h6>${u2} - ${data['scores'][u2]}</h6>`                        
        } else if (Object.keys(data).includes("success") ){
            if (data['success']){
                if (data['correct']){
                    d.innerHTML = `<h4>Correct!</h4>`
                } else{
                    d.innerHTML = `<h4>Incorrect!</h4>`
                }
            } else{
                d.innerHTML = `<h4>Error</h4><hr><h6>${data['error']}</h6>`
            }
        
        } else if (Object.keys(data).includes("message") ){
            if (data['message'].includes('incorrectly') || data['message'].includes('correctly')){
                document.querySelector("input").disabled = false;
                document.querySelector("input").focus();
            }
            d.innerHTML = `<h4>Message</h4><hr><h6>${data['message']}</h6>`
        } else if (Object.keys(data).includes("winner") ){
            gameOver = true;
            u1 = Object.keys(data['ratings'])[0]
            u2 = Object.keys(data['ratings'])[1]
            d.innerHTML = `<h4>Game Over</h4><hr><h5>Winner: ${data['winner']}<hr><h6>New Ratings:<br>${u1} - ${data['ratings'][u1]}<br>${u2} - ${data['ratings'][u2]}<hr><a href='/'>Return Home</a> or <a href='' onclick="location.reload()"">Play Again</a>`
        } else{
            document.querySelector("input").disabled = false;
            document.querySelector("input").focus()
            
            d.innerHTML = `<h4>Question ${data['problem']}</h4><hr><h6>${data['question']}</h6>`
            if (data['answer_choices']){
                d.innerHTML = d.innerHTML + "<ul>"
                for (let choice of data['answer_choices']) {
                    d.innerHTML = d.innerHTML + `<li>${choice}</li>`
                }
            }
        }
        
        document.querySelector("#msgs").appendChild(d)
        window.scrollTo(0, document.body.scrollHeight);
    };

    socket.onopen = function(event){
        socket.send(JSON.stringify({'type': 'join', 'sid': sid, 'code': code}))
    }
    
    socket.onclose = function(event) {
        if (!gameOver){
            d = document.createElement("div");        
            d.classList.add('bubble-opponent');
            d.appendChild(document.createTextNode("Error. Connection to server lost. "))
            d.innerHTML = d.innerHTML + "<a href='/'>Return Home</a>"
            
            document.querySelector("#msgs").appendChild(d)   
            window.scrollTo(0, document.body.scrollHeight);
        }
    }
    document.querySelector("input").disabled = true;
}

function initGame(){
    $("#modal").modal('hide');
    gameOver = false;
    socket = new WebSocket("wss://ws.animaliaga.me");
    var r = 0;
    socket.onmessage = function(event) {
        document.querySelector("input").disabled = true;
        if (r == 0) {
            data = JSON.parse(event.data)
            code = data['gameid']
            document.querySelector("#gameid").innerText = 'Game ID: ' + data['gameid']
            document.querySelector("#inviteLink").innerText = window.location.href + '?gameid=' + data['gameid']
            document.querySelector("#inviteLink").href = window.location.href + '?gameid=' + data['gameid']
            r = r + 1;
            return
        }
        else if (r == 1) {
            document.querySelector("#inviteLink").parentElement.remove();
            document.querySelector("#reopen").parentElement.remove()
            r = r + 1;
        }
        data = JSON.parse(event.data)
        d = document.createElement('div');
        d.classList.add('bubble-opponent');
        if (Object.keys(data).includes("success") ){
            if (data['success']){
                if (data['correct']){
                    d.innerHTML = `<h4>Correct!</h4>`
                } else{
                    d.innerHTML = `<h4>Incorrect!</h4>`
                }
            } else{
                d.innerHTML = `<h4>Error</h4><hr><h6>${data['error']}</h6>`
            }
        } else if (Object.keys(data).includes("winner") ){
            gameOver = true;
            u1 = Object.keys(data['ratings'])[0]
            u2 = Object.keys(data['ratings'])[1]
            d.innerHTML = `<h4>Game Over</h4><hr><h5>Winner: ${data['winner']}<hr><h6>New Ratings:<br>${u1} - ${data['ratings'][u1]}<br>${u2} - ${data['ratings'][u2]}<hr><a href='/'>Return Home</a> or <a href='/play'>Play Again</a>`
        } else if (Object.keys(data).includes('scores')){
            u1 = Object.keys(data['scores'])[0]
            u2 = Object.keys(data['scores'])[1]
            d.innerHTML = `<h4>Current Scores</h4><hr><h6>${u1} - ${data['scores'][u1]}</h6><h6>${u2} - ${data['scores'][u2]}</h6>`
        } 
        else if (Object.keys(data).includes("message") ){
            if (data['message'].includes('incorrectly') || data['message'].includes('correctly')){
                document.querySelector("input").disabled = false;
                document.querySelector("input").focus();
            }
            d.innerHTML = `<h4>Message</h4><hr><h6>${data['message']}</h6>`
        } 
        else {
            document.querySelector("input").disabled = false;
            document.querySelector("input").focus();
            d.innerHTML = `<h4>Question ${data['problem']}</h4><hr><h6>${data['question']}</h6>`
            if (data['answer_choices']){
                d.innerHTML = d.innerHTML + "<ul>"
                for (let choice of data['answer_choices']) {
                    d.innerHTML = d.innerHTML + `<li>${choice}</li>`
                }
            }
            
        }
        document.querySelector("#msgs").appendChild(d)
        window.scrollTo(0, document.body.scrollHeight);
    };

    socket.onopen = function(event){
        socket.send(JSON.stringify({'type': 'initiate', 'sid': sid}))
    }
    
    socket.onclose = function(event) {
        if (!gameOver){
            d = document.createElement("div");        
            d.classList.add('bubble-opponent');
            d.appendChild(document.createTextNode("Error. Connection to server lost. "))
            d.innerHTML = d.innerHTML + "<a href='/'>Return Home</a>"
            
            document.querySelector("#msgs").appendChild(d)   
        }
    }
}
function sub(){
    var inp = document.querySelector("input")
    if(inp.value == ''){ return }
    d = document.createElement("div");
    d.classList.add('bubble-self');
    d.appendChild(document.createTextNode(inp.value))
    
    document.querySelector("#msgs").appendChild(d)
    window.scrollTo(0, document.body.scrollHeight);
    document.querySelector("input").disabled = true;
    socket.send(JSON.stringify({'type': 'answerquestion', 'answer': inp.value, 'code': code, 'sid': sid}));
    inp.value = '';
}



document.querySelector('input').addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    sub()
  }
});


