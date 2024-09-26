function handleChange(value){
    if(value){ document.getElementById("btn_search").disabled = false;}
}

function hadleEmailValidation(cart,email){

let body = JSON.stringify({
    cart_id:cart,
    client_email:email
    }) 

function reqListener() {
    if (this.status == 200) {
        location.href = "/seecart/" + cart
    }
    else
    {
        document.getElementById("btn_search_lb").textContent = this.response
        document.getElementById("btn_search_lb").style.display = "block"
    }
}

const req = new XMLHttpRequest();
req.addEventListener("load", reqListener);
req.open("POST", "/authbyemail");
req.setRequestHeader("Content-Type","application/json");
req.send(body);

}


function logOut(){
   
    fetch("/delete_cookie" , {
        method: "GET"

    }).then(function(data){
        if(data.redirected){
            location.href = data.url
        }

    })
}

function redirectTo(urlParam){
    location.href = "/" + urlParam
}