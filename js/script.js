// const form = document.querySelector("form");
// admin_selector = form.querySelector(".admin");
// pass_selector = form.querySelector(".pwd");

// var admin = document.getElementById("admin");
// var icon = document.getElementById("icon");
// form.onclick = (e)=>{
//   pass = document.getElementById("pass");
//   (admin == "") ? error.classList.add("error") : validateadmin();
//   (pass == "") ? error.classList.add("error") : checkPass();
//   e.preventDefault();

//   function validateadmin(){
//     let pattern = /^[a-zA-Z\-]+$/;
//     if(!admin.value.match(pattern)){
//       admin_selector.classList.add("error");
//       admin_selector.classList.remove("error_icon");
//       let errorTxt = admin_selector.querySelector(".error-txt");
//       (admin.value != "") ? errorTxt.innerText = "Enter a valid email address" : errorTxt.innerText = "Email can't be blank";
//     }else{
//       admin_selector.classList.remove("error");
//       admin_selector.classList.add("error_icon");
//     }
//   }

//   function checkPass(){
//     if(pass == ""){
//       pass_selector.classList.add("error");
//       pass_selector.classList.remove("valid");
//     }else{
//       pass_selector.classList.remove("error");
//       pass_selector.classList.add("valid");
//     }
//   }

//   if(!admin_selector.classList.contains("error") && !pass_selector.classList.contains("error")){
//     window.location.href = form.getAttribute("action");
//   }
// }
$("#icon").hide();
function validation (){
  admin=document.myform.admin.value;
  const usernameRegex = /^[A-Za-z]+$/
  if(!usernameRegex.test(admin)){
    $("#icon").show();
    return false;
  }
}