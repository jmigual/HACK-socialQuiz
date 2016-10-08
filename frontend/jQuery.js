function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value;
	});
	return vars;
}

var id = getUrlVars()["id"];
var server = "http://localhost:5000";
$(document).ready(function(){
	$("#emailInput").focus();
	$(document).keypress(function(e){
		if (e.which == 13){
			var email = $("#emailInput").val();
			$.get(server + "/joinroom&idroom="+id+"&email="+email,function(data){
				alert("Data: "+data);
			});
		}
	});
	/*$("button").click(function(){
		$.get(server+"/register",function(data,status){
			alert("Data: " + data + "\nStatus: " + status);
		});
	});*/
});