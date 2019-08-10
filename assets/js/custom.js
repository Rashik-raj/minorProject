function validate()
{
    data=document.getElementById('textarea1').value;
    summaryType=document.getElementById('summaryType').value;
    errorMsg=document.getElementById('errorMsg');
    flag = false;
    if (data==''){
        errorMsg.style.display="block";
        errorMsg.innerHTML="*** You must enter text or URL ***";
        return flag
    }
    if (summaryType==''){
        errorMsg.style.display="block";
        errorMsg.innerHTML="*** You must select the type ***";
        return flag;
    }
    if (data.includes('http') && summaryType=='abstractive'){
        errorMsg.style.display="block";
        errorMsg.innerHTML="*** You cannot select asbtractive for links right now ***";
        return flag;
    }
    return true;
}
$(document).ready(function(){
    $('.modal').modal();
    $('select').formSelect();
    $(".switch-toggle").click(function(){
        $("#extractive").fadeToggle();
        $("#extractiveGraph").fadeToggle();
      });
});