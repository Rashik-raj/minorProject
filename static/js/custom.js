function validate()
{
    data=document.getElementById('textarea1').value;
    errorMsg=document.getElementById('errorMsg');
    flag = false;
    if (data){
        flag = true;
    }
    else{
        errorMsg.style.display="block";
        errorMsg.innerHTML="*** You must enter text or URL ***";
    }
    return flag;
}
$(document).ready(function(){
    $('.modal').modal();
});
$(document).ready(function(){
    $(".switch-toggle").click(function(){
      $("#extractive").fadeToggle();
      $("#abstractive").fadeToggle();
    });
  });